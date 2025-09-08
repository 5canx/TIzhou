"""
用户相关视图
"""
import logging
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import user_passes_test
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, PasswordChangeForm
from apps.core.models import User, SystemLog

# 创建用户日志记录器
user_logger = logging.getLogger('user')


def is_admin(user):
    """检查是否为管理员"""
    return user.is_authenticated and user.is_admin


def is_moderator(user):
    """检查是否为审核员"""
    return user.is_authenticated and user.is_moderator


def register(request):
    """用户注册"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '注册成功！欢迎加入题库管理系统')
            
            # 记录日志
            SystemLog.objects.create(
                user=user,
                log_type='user',
                action='用户注册',
                description=f'新用户 {user.username} 注册成功',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            return redirect('home')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'users/register.html', {'form': form})


def user_login(request):
    """用户登录"""
    # 添加详细的日志记录
    user_logger.info(f'登录请求到达: 方法={request.method}, 路径={request.path}, 用户={request.user if request.user.is_authenticated else "未认证"}')
    
    if request.user.is_authenticated:
        user_logger.info(f'用户已认证，重定向到home')
        return redirect('home')
    
    if request.method == 'POST':
        user_logger.info(f'收到POST登录请求，表单数据: {request.POST}')
        form = UserLoginForm(request, data=request.POST)
        
        # 记录表单验证状态
        user_logger.info(f'表单验证结果: {form.is_valid()}')
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            user_logger.info(f'表单验证通过，尝试认证用户: {username}')
            
            # 尝试使用用户名登录
            user = authenticate(username=username, password=password)
            user_logger.info(f'用户名认证结果: {user}')
            
            # 如果用户名登录失败，尝试使用邮箱登录
            if user is None:
                try:
                    user_obj = User.objects.get(email=username)
                    user = authenticate(username=user_obj.username, password=password)
                    user_logger.info(f'邮箱认证结果: {user}')
                except User.DoesNotExist:
                    user_logger.info(f'邮箱 {username} 不存在')
                    pass
            
            if user is not None:
                login(request, user)
                messages.success(request, f'欢迎回来，{user.username}！')
                
                # 记录日志
                SystemLog.objects.create(
                    user=user,
                    log_type='user',
                    action='用户登录',
                    description=f'用户 {user.username} 登录成功',
                    ip_address=request.META.get('REMOTE_ADDR')
                )
                
                user_logger.info(f'用户 {username} 登录成功', extra={'user_id': user.id})
                
                # 获取next参数或默认值
                next_url = request.GET.get('next', '')
                user_logger.info(f'登录成功，next_url: {next_url}')
                
                # 修复重定向循环问题
                if not next_url or next_url == '/':
                    # 如果next_url为空或指向首页，根据用户角色决定重定向位置
                    if user.is_admin:
                        user_logger.info(f'管理员用户重定向到admin:index')
                        return redirect('admin:index')
                    else:
                        user_logger.info(f'普通用户重定向到home')
                        return redirect('home')
                
                # 确保管理员用户可以正确重定向到管理后台
                if '/admin/' in next_url and user.is_admin:
                    user_logger.info(f'管理员用户重定向到next_url: {next_url}')
                    return redirect(next_url)
                elif '/admin/' in next_url and not user.is_admin:
                    # 非管理员用户尝试访问管理后台，重定向到首页
                    messages.error(request, '您没有权限访问管理后台')
                    user_logger.warning(f'非管理员用户尝试访问管理后台，重定向到home')
                    return redirect('home')
                
                user_logger.info(f'重定向到next_url: {next_url}')
                return redirect(next_url)
            else:
                # 登录失败
                user_logger.warning(f'用户 {username} 登录失败', extra={'ip_address': request.META.get('REMOTE_ADDR')})
                messages.error(request, '账号或密码错误，请重试')
    else:
        form = UserLoginForm()
        user_logger.info(f'GET请求，显示登录页面')
    
    # 如果是GET请求或表单验证失败，显示登录页面
    context = {
        'form': form
    }
    user_logger.info(f'渲染登录页面，next参数: {request.GET.get("next", "")}')
    return render(request, 'users/login.html', context)


@login_required
def user_logout(request):
    """用户登出"""
    # 记录日志
    SystemLog.objects.create(
        user=request.user,
        log_type='user',
        action='用户登出',
        description=f'用户 {request.user.username} 登出',
        ip_address=request.META.get('REMOTE_ADDR')
    )
    
    logout(request)
    messages.info(request, '您已成功登出')
    return redirect('login')


@login_required
def profile(request):
    """用户资料"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '资料更新成功！')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'users/profile.html', {'form': form})


@login_required
def change_password(request):
    """修改密码"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '密码修改成功！')
            
            # 记录日志
            SystemLog.objects.create(
                user=request.user,
                log_type='user',
                action='修改密码',
                description=f'用户 {request.user.username} 修改密码',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'users/change_password.html', {'form': form})


@user_passes_test(is_admin)
def user_management(request):
    """用户管理（仅管理员）"""
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'users/user_management.html', {'users': users})


@user_passes_test(is_admin)
def toggle_user_status(request, user_id):
    """切换用户状态（仅管理员）"""
    try:
        user = User.objects.get(id=user_id)
        user.is_active = not user.is_active
        user.save()
        
        action = '启用' if user.is_active else '禁用'
        messages.success(request, f'用户 {user.username} 已{action}')
        
        # 记录日志
        SystemLog.objects.create(
            user=request.user,
            log_type='user',
            action=f'{action}用户',
            description=f'管理员 {request.user.username} {action}了用户 {user.username}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
    except User.DoesNotExist:
        messages.error(request, '用户不存在')
    
    return redirect('user_management')


@user_passes_test(is_admin)
def change_user_role(request, user_id):
    """修改用户角色（仅管理员）"""
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id)
            new_role = request.POST.get('role')
            if new_role in ['admin', 'moderator', 'user']:
                old_role = user.role
                user.role = new_role
                user.save()
                
                messages.success(request, f'用户 {user.username} 角色已修改为 {new_role}')
                
                # 记录日志
                SystemLog.objects.create(
                    user=request.user,
                    log_type='user',
                    action='修改用户角色',
                    description=f'管理员 {request.user.username} 将用户 {user.username} 的角色从 {old_role} 修改为 {new_role}',
                    ip_address=request.META.get('REMOTE_ADDR')
                )
            else:
                messages.error(request, '无效的角色')
        except User.DoesNotExist:
            messages.error(request, '用户不存在')
    
    return redirect('user_management')


@csrf_exempt
def api_login(request):
    """API登录接口"""
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        user = authenticate(username=username, password=password)
        if user is None:
            # 尝试用邮箱登录
            try:
                user_obj = User.objects.get(email=username)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        
        if user is not None and user.is_active:
            login(request, user)
            return JsonResponse({
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'is_admin': user.is_admin,
                    'is_moderator': user.is_moderator
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'error': '用户名或密码错误'
            })
    
    return JsonResponse({'error': '仅支持POST请求'}, status=405)