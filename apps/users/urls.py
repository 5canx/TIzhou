from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # 认证相关
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # 用户资料
    path('profile/', views.profile, name='profile'),
    path('change-password/', views.change_password, name='change_password'),
    
    # 用户管理（仅管理员）
    path('management/', views.user_management, name='user_management'),
    path('toggle-status/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),
    path('change-role/<int:user_id>/', views.change_user_role, name='change_user_role'),
    
    # API接口
    path('api/login/', views.api_login, name='api_login'),
] 