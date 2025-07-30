"""
题目审核相关视图
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from apps.core.models import QuestionSubmission, SystemLog, User
from apps.users.views import is_moderator
from utils.elasticsearch_utils import ElasticsearchService
import json


@login_required
@user_passes_test(is_moderator)
def submission_list(request):
    """题目提交列表"""
    status_filter = request.GET.get('status', '')
    page = request.GET.get('page', 1)
    
    submissions = QuestionSubmission.objects.all()
    
    if status_filter:
        submissions = submissions.filter(status=status_filter)
    
    # 分页
    paginator = Paginator(submissions, 20)
    submissions_page = paginator.get_page(page)
    
    context = {
        'submissions': submissions_page,
        'status_filter': status_filter,
        'status_choices': QuestionSubmission.STATUS_CHOICES,
    }
    
    return render(request, 'moderator/submission_list.html', context)


@login_required
@user_passes_test(is_moderator)
def submission_detail(request, submission_id):
    """题目提交详情"""
    submission = get_object_or_404(QuestionSubmission, id=submission_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        comment = request.POST.get('comment', '')
        
        if action == 'approve':
            submission.approve(request.user, comment)
            messages.success(request, '题目已审核通过')
            
            # 记录日志
            SystemLog.objects.create(
                user=request.user,
                log_type='question',
                action='审核通过题目',
                description=f'审核员 {request.user.username} 通过了题目 "{submission.title}"',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
        elif action == 'reject':
            submission.reject(request.user, comment)
            messages.warning(request, '题目已拒绝')
            
            # 记录日志
            SystemLog.objects.create(
                user=request.user,
                log_type='question',
                action='拒绝题目',
                description=f'审核员 {request.user.username} 拒绝了题目 "{submission.title}"，原因：{comment}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
        
        return redirect('moderator:submission_list')
    
    context = {
        'submission': submission,
    }
    
    return render(request, 'moderator/submission_detail.html', context)


@login_required
@user_passes_test(is_moderator)
def bulk_approve(request):
    """批量审核通过"""
    if request.method == 'POST':
        submission_ids = request.POST.getlist('submission_ids')
        comment = request.POST.get('comment', '')
        
        approved_count = 0
        for submission_id in submission_ids:
            try:
                submission = QuestionSubmission.objects.get(id=submission_id, status='pending')
                submission.approve(request.user, comment)
                approved_count += 1
                
                # 记录日志
                SystemLog.objects.create(
                    user=request.user,
                    log_type='question',
                    action='批量审核通过',
                    description=f'审核员 {request.user.username} 批量通过了题目 "{submission.title}"',
                    ip_address=request.META.get('REMOTE_ADDR')
                )
            except QuestionSubmission.DoesNotExist:
                continue
        
        messages.success(request, f'成功审核通过 {approved_count} 个题目')
    
    return redirect('moderator:submission_list')


@login_required
@user_passes_test(is_moderator)
def bulk_reject(request):
    """批量审核拒绝"""
    if request.method == 'POST':
        submission_ids = request.POST.getlist('submission_ids')
        comment = request.POST.get('comment', '')
        
        rejected_count = 0
        for submission_id in submission_ids:
            try:
                submission = QuestionSubmission.objects.get(id=submission_id, status='pending')
                submission.reject(request.user, comment)
                rejected_count += 1
                
                # 记录日志
                SystemLog.objects.create(
                    user=request.user,
                    log_type='question',
                    action='批量拒绝题目',
                    description=f'审核员 {request.user.username} 批量拒绝了题目 "{submission.title}"，原因：{comment}',
                    ip_address=request.META.get('REMOTE_ADDR')
                )
            except QuestionSubmission.DoesNotExist:
                continue
        
        messages.warning(request, f'成功拒绝 {rejected_count} 个题目')
    
    return redirect('moderator:submission_list')


@login_required
@user_passes_test(is_moderator)
def index_approved_questions(request):
    """将已审核通过的题目索引到ES"""
    if request.method == 'POST':
        es_service = ElasticsearchService()
        
        # 获取所有已审核通过但未索引的题目
        approved_submissions = QuestionSubmission.objects.filter(
            status='approved',
            is_indexed=False
        )
        
        indexed_count = 0
        for submission in approved_submissions:
            try:
                # 准备ES文档
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
                
                # 索引到ES
                success, failed = es_service.bulk_index([doc])
                if success > 0:
                    submission.is_indexed = True
                    submission.es_id = str(submission.id)
                    submission.save()
                    indexed_count += 1
                    
                    # 记录日志
                    SystemLog.objects.create(
                        user=request.user,
                        log_type='question',
                        action='索引题目到ES',
                        description=f'审核员 {request.user.username} 将题目 "{submission.title}" 索引到ES',
                        ip_address=request.META.get('REMOTE_ADDR')
                    )
                
            except Exception as e:
                messages.error(request, f'索引题目 {submission.id} 失败: {str(e)}')
        
        messages.success(request, f'成功索引 {indexed_count} 个题目到ES')
    
    return redirect('moderator:submission_list')


@csrf_exempt
@login_required
@user_passes_test(is_moderator)
def api_approve_submission(request, submission_id):
    """API审核通过题目"""
    if request.method == 'POST':
        try:
            submission = QuestionSubmission.objects.get(id=submission_id)
            data = json.loads(request.body)
            comment = data.get('comment', '')
            
            submission.approve(request.user, comment)
            
            # 记录日志
            SystemLog.objects.create(
                user=request.user,
                log_type='question',
                action='API审核通过',
                description=f'审核员 {request.user.username} 通过API审核通过了题目 "{submission.title}"',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            return JsonResponse({
                'success': True,
                'message': '题目审核通过'
            })
        except QuestionSubmission.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': '题目不存在'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'error': '仅支持POST请求'}, status=405)


@csrf_exempt
@login_required
@user_passes_test(is_moderator)
def api_reject_submission(request, submission_id):
    """API拒绝题目"""
    if request.method == 'POST':
        try:
            submission = QuestionSubmission.objects.get(id=submission_id)
            data = json.loads(request.body)
            comment = data.get('comment', '')
            
            submission.reject(request.user, comment)
            
            # 记录日志
            SystemLog.objects.create(
                user=request.user,
                log_type='question',
                action='API拒绝题目',
                description=f'审核员 {request.user.username} 通过API拒绝了题目 "{submission.title}"，原因：{comment}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            return JsonResponse({
                'success': True,
                'message': '题目已拒绝'
            })
        except QuestionSubmission.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': '题目不存在'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'error': '仅支持POST请求'}, status=405) 