"""
Production settings for djangoProject project.
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# 安全设置
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# 生产环境静态文件配置
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = []

# 生产环境媒体文件配置
MEDIA_ROOT = os.environ.get('MEDIA_ROOT', BASE_DIR / 'media') 