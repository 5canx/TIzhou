"""
Django settings for djangoProject project.
"""

from pathlib import Path
import os
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-@otcs3@c^e8-me906gybmq9ks2*f5k(z!6_is707w-15xpgn@v')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'colorfield',
    # 自定义应用
    'apps.core.apps.CoreConfig',
    'apps.users.apps.UsersConfig',
    'apps.moderator.apps.ModeratorConfig',
    'apps.questions.apps.QuestionsConfig',
    'apps.upload.apps.UploadConfig',
    'apps.search.apps.SearchConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'djangoProject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'djangoProject.wsgi.application'

# Database - 使用SQLite作为Django内置功能的轻量级存储
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Cache - 使用Redis作为缓存
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': f"redis://{os.environ.get('REDIS_HOST', 'localhost')}:{os.environ.get('REDIS_PORT', 6379)}/1",
        'OPTIONS': {
            'PASSWORD': os.environ.get('REDIS_PASSWORD', '123456'),
        }
    }
}

# Session - 使用Redis存储会话
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 自定义用户模型
AUTH_USER_MODEL = 'core.User'

# Redis配置
REDIS_CONFIG = {
    'HOST': os.environ.get('REDIS_HOST', 'localhost'),
    'PORT': int(os.environ.get('REDIS_PORT', 6379)),
    'DB': int(os.environ.get('REDIS_DB', 3)),
    'PASSWORD': os.environ.get('REDIS_PASSWORD', '123456'),
    'DECODE_RESPONSES': True,
    'SOCKET_TIMEOUT': 5
}

# Elasticsearch配置
ES_CONFIG = {
    'HOST': os.environ.get('ES_HOST', 'http://localhost:9200'),
    'INDEX_NAME': os.environ.get('ES_INDEX_NAME', 'questions'),
    'TIMEOUT': int(os.environ.get('ES_TIMEOUT', 30))
}

# 字段映射配置
FIELD_MAPPINGS = {
    '题目编号': 'question_id',
    '题目': 'content',
    '题目内容': 'content',
    '题型': 'question_type',
    '难度': 'difficulty',
    '答案': 'answer',
    '选项A': 'options.0.text',
    '选项A图片': 'options.0.image',
    '选项B': 'options.1.text',
    '选项B图片': 'options.1.image',
    '选项C': 'options.2.text',
    '选项C图片': 'options.2.image',
    '选项D': 'options.3.text',
    '选项D图片': 'options.3.image'
}

ALLOWED_FIELDS = list(FIELD_MAPPINGS.values()) + [
    'explanation',
    'source',
    'ingest_time'
]

# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# 文件上传配置
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# 缓存配置
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': f"redis://{REDIS_CONFIG['HOST']}:{REDIS_CONFIG['PORT']}/{REDIS_CONFIG['DB']}",
        'OPTIONS': {
            'PASSWORD': REDIS_CONFIG['PASSWORD'],
        }
    }
} 