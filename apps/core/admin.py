# apps/core/admin.py
from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User, QuestionSubmission, SystemLog, ESQuestionDummy
from utils.elasticsearch_utils import ElasticsearchService


class CustomUserAdmin(UserAdmin):
    """自定义用户管理"""
    list_display = ('username', 'email', 'role', 'is_active', 'date_joined', 'last_login')
    list_filter = ('role', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    fieldsets = UserAdmin.fieldsets + (
        ('额外信息', {'fields': ('role', 'phone', 'avatar')}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('额外信息', {'fields': ('role', 'phone', 'email')}),
    )


class QuestionSubmissionAdmin(admin.ModelAdmin):
    """题目提交管理"""
    list_display = ('title', 'submitter', 'question_type', 'difficulty', 'status', 'created_at', 'reviewer')
    list_filter = ('status', 'question_type', 'difficulty', 'created_at')
    search_fields = ('title', 'content', 'submitter__username')
    readonly_fields = ('created_at', 'updated_at', 'review_time')
    ordering = ('-created_at',)

    fieldsets = (
        ('基本信息', {
            'fields': ('submitter', 'title', 'content', 'question_type', 'difficulty')
        }),
        ('答案和选项', {
            'fields': ('answer', 'explanation', 'options', 'source')
        }),
        ('审核信息', {
            'fields': ('status', 'reviewer', 'review_time', 'review_comment')
        }),
        ('ES信息', {
            'fields': ('es_id', 'is_indexed'),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['approve_selected', 'reject_selected', 'index_to_es']

    def approve_selected(self, request, queryset):
        """批量审核通过"""
        count = 0
        for submission in queryset.filter(status='pending'):
            submission.approve(request.user, '批量审核通过')
            count += 1
        self.message_user(request, f'成功审核通过 {count} 个题目')

    approve_selected.short_description = '批量审核通过'

    def reject_selected(self, request, queryset):
        """批量审核拒绝"""
        count = 0
        for submission in queryset.filter(status='pending'):
            submission.reject(request.user, '批量审核拒绝')
            count += 1
        self.message_user(request, f'成功拒绝 {count} 个题目')

    reject_selected.short_description = '批量审核拒绝'

    def index_to_es(self, request, queryset):
        """索引到ES"""
        es_service = ElasticsearchService()
        count = 0
        for submission in queryset.filter(status='approved', is_indexed=False):
            try:
                doc = {
                    'question_id': submission.id,
                    'content': submission.content,
                    'question_type': submission.question_type,
                    'difficulty': submission.difficulty,
                    'answer': submission.answer,
                    'explanation': submission.explanation or '',
                    'options': submission.options,
                    'source': submission.source or '',
                    'ingest_time': submission.created_at.isoformat()
                }
                success, failed = es_service.bulk_index([doc])
                if success > 0:
                    submission.is_indexed = True
                    submission.es_id = str(submission.id)
                    submission.save()
                    count += 1
            except Exception as e:
                self.message_user(request, f'索引题目 {submission.id} 失败: {str(e)}', level='ERROR')
        self.message_user(request, f'成功索引 {count} 个题目到ES')

    index_to_es.short_description = '索引到ES'


class SystemLogAdmin(admin.ModelAdmin):
    """系统日志管理"""
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
    """自定义管理站点"""
    site_header = "题库管理系统"
    site_title = "题库管理"
    index_title = "管理首页"

    def index(self, request, extra_context=None):
        """自定义管理首页"""
        extra_context = extra_context or {}
        extra_context['questions'] = QuestionSubmission.objects.all().select_related('submitter', 'reviewer')
        return super().index(request, extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('es_questions/', self.admin_view(self.es_questions_view), name='es_questions'),
            path('dashboard/', self.admin_view(self.dashboard_view), name='dashboard'),
        ]
        return custom_urls + urls

    def es_questions_view(self, request):
        """ES题目管理视图"""
        try:
            es_service = ElasticsearchService()
            result = es_service.list_all(size=50)
            questions = [hit['_source'] for hit in result.get('hits', [])]
            return render(request, 'admin/es_questions.html', {'questions': questions})
        except Exception as e:
            return render(request, 'admin/es_questions.html', {'error': str(e)})

    def dashboard_view(self, request):
        """仪表板视图"""
        from django.db.models import Count
        from django.utils import timezone
        from datetime import timedelta

        # 统计数据
        total_users = User.objects.count()
        total_submissions = QuestionSubmission.objects.count()
        pending_submissions = QuestionSubmission.objects.filter(status='pending').count()
        approved_submissions = QuestionSubmission.objects.filter(status='approved').count()

        # 最近7天的数据
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent_users = User.objects.filter(date_joined__gte=seven_days_ago).count()
        recent_submissions = QuestionSubmission.objects.filter(created_at__gte=seven_days_ago).count()

        # 按状态统计
        status_stats = QuestionSubmission.objects.values('status').annotate(count=Count('id'))

        context = {
            'total_users': total_users,
            'total_submissions': total_submissions,
            'pending_submissions': pending_submissions,
            'approved_submissions': approved_submissions,
            'recent_users': recent_users,
            'recent_submissions': recent_submissions,
            'status_stats': status_stats,
        }

        return render(request, 'admin/dashboard.html', context)


# 实例化自定义 AdminSite
custom_admin_site = CustomAdminSite(name='custom_admin')

# 为自定义管理站点注册模型
custom_admin_site.register(User, CustomUserAdmin)
custom_admin_site.register(QuestionSubmission, QuestionSubmissionAdmin)
custom_admin_site.register(SystemLog, SystemLogAdmin)