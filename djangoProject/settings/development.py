"""
Development settings for djangoProject project.
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# 开发环境缓存配置
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# 开发环境静态文件配置
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# 开发环境媒体文件配置
MEDIA_ROOT = BASE_DIR / 'media' 