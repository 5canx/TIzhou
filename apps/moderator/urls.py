from django.urls import path
from . import views

app_name = 'moderator'

urlpatterns = [
    # 题目审核
    path('submissions/', views.submission_list, name='submission_list'),
    path('submissions/<int:submission_id>/', views.submission_detail, name='submission_detail'),
    path('bulk-approve/', views.bulk_approve, name='bulk_approve'),
    path('bulk-reject/', views.bulk_reject, name='bulk_reject'),
    path('index-approved/', views.index_approved_questions, name='index_approved_questions'),
    
    # API接口
    path('api/approve/<int:submission_id>/', views.api_approve_submission, name='api_approve_submission'),
    path('api/reject/<int:submission_id>/', views.api_reject_submission, name='api_reject_submission'),
] 