from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class BaseModel(models.Model):
    """基础模型"""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        abstract = True


class User(AbstractUser):
    """自定义用户模型"""
    ROLE_CHOICES = (
        ('admin', '管理员'),
        ('moderator', '审核员'),
        ('user', '普通用户'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user', verbose_name='用户角色')
    phone = models.CharField(max_length=11, blank=True, null=True, verbose_name='手机号')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='头像')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
        db_table = 'auth_user'

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_moderator(self):
        return self.role in ['admin', 'moderator']


class QuestionSubmission(BaseModel):
    """题目提交模型"""
    STATUS_CHOICES = (
        ('pending', '待审核'),
        ('approved', '已通过'),
        ('rejected', '已拒绝'),
    )
    
    submitter = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='提交者')
    title = models.CharField(max_length=200, verbose_name='题目标题')
    content = models.TextField(verbose_name='题目内容')
    question_type = models.CharField(max_length=50, verbose_name='题型')
    difficulty = models.CharField(max_length=20, verbose_name='难度')
    answer = models.TextField(verbose_name='答案')
    explanation = models.TextField(blank=True, null=True, verbose_name='解析')
    options = models.JSONField(default=list, verbose_name='选项')
    source = models.CharField(max_length=100, blank=True, null=True, verbose_name='来源')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='审核状态')
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='reviewed_questions', verbose_name='审核员')
    review_time = models.DateTimeField(blank=True, null=True, verbose_name='审核时间')
    review_comment = models.TextField(blank=True, null=True, verbose_name='审核意见')
    
    # ES相关字段
    es_id = models.CharField(max_length=50, blank=True, null=True, verbose_name='ES文档ID')
    is_indexed = models.BooleanField(default=False, verbose_name='是否已索引')
    
    class Meta:
        verbose_name = '题目提交'
        verbose_name_plural = '题目提交'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.submitter.username}"

    def approve(self, reviewer, comment=""):
        """审核通过"""
        self.status = 'approved'
        self.reviewer = reviewer
        self.review_time = timezone.now()
        self.review_comment = comment
        self.save()

    def reject(self, reviewer, comment=""):
        """审核拒绝"""
        self.status = 'rejected'
        self.reviewer = reviewer
        self.review_time = timezone.now()
        self.review_comment = comment
        self.save()


class ESQuestionDummy(models.Model):
    """ES题目虚拟模型"""
    class Meta:
        verbose_name = "ES 题库"
        verbose_name_plural = "ES 题库"
        managed = False  # 不创建表


class SystemLog(BaseModel):
    """系统日志模型"""
    LOG_TYPES = (
        ('user', '用户操作'),
        ('question', '题目操作'),
        ('system', '系统操作'),
    )
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='操作用户')
    log_type = models.CharField(max_length=20, choices=LOG_TYPES, verbose_name='日志类型')
    action = models.CharField(max_length=100, verbose_name='操作')
    description = models.TextField(verbose_name='描述')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='IP地址')
    
    class Meta:
        verbose_name = '系统日志'
        verbose_name_plural = '系统日志'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.action} - {self.created_at}" 