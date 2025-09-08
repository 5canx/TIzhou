from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import render
from .models import User, QuestionSubmission, QuestionSubmissionReview, SystemLog
from utils.elasticsearch_utils import ElasticsearchService
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
import uuid
import datetime


class QuestionSubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'submitter', 'question_type', 'difficulty', 'status', 'created_at', 'reviewer')
    list_filter = ('status', 'question_type', 'difficulty', 'created_at')
    search_fields = ('title', 'content', 'submitter__username')
    readonly_fields = ('created_at', 'updated_at', 'review_time')
    ordering = ('-created_at',)

    actions = ['approve_selected', 'reject_selected', 'index_to_es']

    def approve_selected(self, request, queryset):
        count = 0
        for submission in queryset.filter(status='pending'):
            submission.approve(request.user, '批量审核通过')
            count += 1
        self.message_user(request, f'成功审核通过 {count} 个题目')

    approve_selected.short_description = '批量审核通过'

    def reject_selected(self, request, queryset):
        count = 0
        for submission in queryset.filter(status='pending'):
            submission.reject(request.user, '批量审核拒绝')
            count += 1
        self.message_user(request, f'成功拒绝 {count} 个题目')

    reject_selected.short_description = '批量审核拒绝'

    def index_to_es(self, request, queryset):
        es_service = ElasticsearchService()
        count = 0
        for submission in queryset.filter(status='approved', is_indexed=False):
            try:
                # 自动生成唯一的ES文档ID
                # 格式: question_{用户ID}_{时间戳}_{随机字符串}
                timestamp = int(datetime.datetime.now().timestamp())
                random_str = uuid.uuid4().hex[:6]
                es_id = f"question_{submission.submitter.id}_{timestamp}_{random_str}"
                
                doc = {
                    'question_id': es_id,
                    'content': submission.content,
                    'question_type': submission.question_type,
                    'difficulty': submission.difficulty,
                    'answer': submission.answer,
                    'explanation': submission.explanation or '',
                    'options': submission.options,
                    'source': submission.source or '',
                    'ingest_time': datetime.datetime.now().isoformat()
                }
                
                # 直接使用ES的create方法，指定文档ID
                es_service.es.create(
                    index=es_service.index_name,
                    id=es_id,
                    body=doc
                )
                
                submission.is_indexed = True
                submission.es_id = es_id
                submission.save()
                count += 1
                
            except Exception as e:
                self.message_user(request, f'索引题目 {submission.id} 失败: {str(e)}', level='ERROR')
        self.message_user(request, f'成功索引 {count} 个题目到ES')

    index_to_es.short_description = '索引到ES'


class QuestionSubmissionReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'submitter', 'question_type', 'difficulty', 'created_at')
    list_filter = ('question_type', 'difficulty', 'created_at')
    search_fields = ('title', 'content', 'submitter__username')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(status='pending')


class SystemLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'log_type', 'action', 'created_at', 'ip_address')
    list_filter = ('log_type', 'action', 'created_at')
    search_fields = ('user__username', 'action', 'description')
    readonly_fields = ('user', 'log_type', 'action', 'description', 'ip_address', 'created_at')
    ordering = ('-created_at',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class CustomAdminSite(admin.AdminSite):
    site_header = "题舟 - 管理后台"
    site_title = "题舟 - 管理后台"
    index_title = "管理首页"
    template_name = 'admin/custom_admin/index.html'
    
    def login(self, request, extra_context=None):
        """重写登录方法，重定向到用户登录页面"""
        # 构建重定向URL，包含next参数指向管理后台
        from django.urls import reverse
        from django.shortcuts import redirect
        next_url = request.GET.get('next', reverse('admin:index'))
        user_login_url = reverse('users:login') + '?next=' + next_url
        return redirect(user_login_url)
    
    def each_context(self, request):
        """添加自定义CSS文件"""
        context = super().each_context(request)
        context['extra_css'] = ['css/admin_custom.css']
        return context

    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        for app in app_list:
            if app['app_label'] == 'core':
                app['name'] = ''
        app_list.append({
            'name': '题目管理',
            'app_label': 'question_management',
            'models': [{
                'name': '所有题目',
                'object_name': 'QuestionSubmission',
                'admin_url': reverse('admin:question-management'),
                'add_url': '',
                'icon': 'fas fa-question-circle',
            }]
        })
        return app_list

    def delete_questions_view(self, request):
        if request.method == 'POST':
            try:
                import json
                question_ids = json.loads(request.POST.get('question_ids', '[]'))
                
                if not question_ids:
                    return JsonResponse({'success': False, 'error': '没有选择要删除的题目'})
                
                es_service = ElasticsearchService()
                deleted_count = 0
                
                for question_id in question_ids:
                    try:
                        # 从ES中删除文档
                        es_service.es.delete(index=es_service.index_name, id=question_id, ignore=[404])
                        deleted_count += 1
                        
                        # 更新数据库中的记录
                        QuestionSubmission.objects.filter(es_id=question_id, is_indexed=True).update(
                            is_indexed=False,
                            es_id=None
                        )
                    except Exception as e:
                        print(f"删除题目 {question_id} 失败: {str(e)}")
                
                # 记录操作日志
                SystemLog.objects.create(
                    user=request.user,
                    log_type='question',
                    action='删除题目',
                    description=f'删除了 {deleted_count} 个题目',
                    ip_address=request.META.get('REMOTE_ADDR')
                )
                
                return JsonResponse({'success': True, 'deleted': deleted_count})
            except Exception as e:
                print(f"删除题目失败: {str(e)}")
                return JsonResponse({'success': False, 'error': str(e)})
        
        return JsonResponse({'success': False, 'error': '仅支持POST请求'})
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('question-management/', self.admin_view(self.question_management_view), name='question-management'),
            path('es-questions/', self.admin_view(self.es_questions_view), name='es_questions'),
            path('dashboard/', self.admin_view(self.dashboard_view), name='dashboard'),
            path('delete-questions/', self.admin_view(self.delete_questions_view), name='delete_questions'),
        ]
        return custom_urls + urls

    def question_management_view(self, request):
        try:
            es_service = ElasticsearchService()

            page_size = 20
            page = request.GET.get('page', 1)
            try:
                page = int(page)
                if page < 1:
                    page = 1
            except ValueError:
                page = 1

            from_ = (page - 1) * page_size
            result = es_service.list_all(from_=from_, size=page_size)

            hits_container = result.get('hits')
            if isinstance(hits_container, dict):
                hits = hits_container.get('hits', [])
                total = hits_container.get('total', {}).get('value', 0)
            elif isinstance(hits_container, list):
                hits = hits_container
                total = len(hits)
            else:
                hits = []
                total = 0

            questions = [hit.get('_source', {}) for hit in hits]

            paginator = Paginator(range(total), page_size)
            try:
                page_obj = paginator.page(page)
            except (PageNotAnInteger, EmptyPage):
                page_obj = paginator.page(1)
            print("ES 返回结果：", result)
            hits_container = result.get('hits')
            print("hits_container:", hits_container)
            if isinstance(hits_container, dict):
                hits = hits_container.get('hits', [])
                total = hits_container.get('total', {}).get('value', 0)
            elif isinstance(hits_container, list):
                hits = hits_container
                total = len(hits)
            else:
                hits = []
                total = 0
            print(f"总题数: {total}, 当前页题数: {len(hits)}")
            print(f"当前页: {page_obj.number}, 总页数: {paginator.num_pages}, 是否有下一页: {page_obj.has_next()}")
            context = {
                'questions': questions,
                'paginator': paginator,
                'page_obj': page_obj,
                'total': total,
                'page_size': page_size,
            }

            # 如果是 AJAX 请求，只返回 table 内容部分
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('admin/_question_table.html', context, request=request)
                return HttpResponse(html)

            return render(request, 'admin/question_management.html', context)

        except Exception as e:
            print("错误信息:", e)
            return render(request, 'admin/question_management.html', {'error': str(e)})

    def es_questions_view(self, request):
        return render(request, 'admin/es_questions.html', {})
    def dashboard_view(self, request):
        from django.shortcuts import render
        from django.db.models import Count
        
        # 获取统计数据
        total_users = User.objects.count()
        total_submissions = QuestionSubmission.objects.count()
        pending_submissions = QuestionSubmission.objects.filter(status='pending').count()
        approved_submissions = QuestionSubmission.objects.filter(status='approved').count()
        
        # 获取最近的系统日志
        recent_logs = SystemLog.objects.order_by('-created_at')[:10]
        
        # 获取应用列表
        app_list = self.get_app_list(request)
        
        context = {
            'total_users': total_users,
            'total_submissions': total_submissions,
            'pending_submissions': pending_submissions,
            'approved_submissions': approved_submissions,
            'recent_logs': recent_logs,
            'app_list': app_list,
            'has_permission': True
        }
        
        return render(request, 'admin/custom_admin/index.html', context)


custom_admin_site = CustomAdminSite(name='custom_admin')

custom_admin_site.register(User)
custom_admin_site.register(QuestionSubmission, QuestionSubmissionAdmin)
custom_admin_site.register(QuestionSubmissionReview, QuestionSubmissionReviewAdmin)
custom_admin_site.register(SystemLog, SystemLogAdmin)


# def question_management_view(self, request):
#     try:
#         es_service = ElasticsearchService()
#
#         page_size = 20  # 每页显示数量
#         page = request.GET.get('page', 1)
#         try:
#             page = int(page)
#             if page < 1:
#                 page = 1
#         except ValueError:
#             page = 1
#
#         # 计算 from 参数
#         from_ = (page - 1) * page_size
#         # 调用 ES，支持分页
#         result = es_service.list_all(from_=from_, size=page_size)
#
#         hits_container = result.get('hits')
#         if isinstance(hits_container, dict):
#             hits = hits_container.get('hits', [])
#             total = hits_container.get('total', {}).get('value', 0)
#         elif isinstance(hits_container, list):
#             hits = hits_container
#             total = len(hits)
#         else:
#             hits = []
#             total = 0
#
#         questions = [hit.get('_source', {}) for hit in hits]
#
#         # Django 分页器，用于模板渲染分页导航
#         paginator = Paginator(range(total), page_size)  # 这里只用总数生成分页
#         try:
#             page_obj = paginator.page(page)
#         except (PageNotAnInteger, EmptyPage):
#             page_obj = paginator.page(1)
#
#         context = {
#             'questions': questions,
#             'paginator': paginator,
#             'page_obj': page_obj,
#             'total': total,
#             'page_size': page_size,
#         }
#
#         return render(request, 'admin/question_management.html', context)
#
#     except Exception as e:
#         print("错误信息:", e)
#         return render(request, 'admin/question_management.html', {'error': str(e)})