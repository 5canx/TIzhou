from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-@otcs3@c^e8-me906gybmq9ks2*f5k(z!6_is707w-15xpgn@v'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    "jazzmin",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'index.apps.IndexConfig',
    'colorfield',
]
ADMIN_INTERFACE = {
    'THEME': 'orange',
    'LOGO': 'path/to/your/logo.png'
}
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
        'APP_DIRS': True,  # 恢复默认启用 app 内模板加载
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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/staticfiles/'  # 对外访问的 URL 路径
STATICFILES_DIRS = [
    BASE_DIR / 'staticfiles',  # 这里是开发环境中额外的静态文件目录，包含你自己项目的静态文件
]

# 这里是你存放静态文件的路径

# # 媒体文件配置
# MEDIA_URL = '/media/'  # 媒体文件的 URL 路径
# MEDIA_ROOT = BASE_DIR / 'media'  # 媒体文件的存储路径

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REDIS_CONFIG = {
    'HOST': 'localhost',
    'PORT': 6379,
    'DB': 3,
    'PASSWORD': '123456',  # 注意密码改为字符串类型
    'DECODE_RESPONSES': True,
    'SOCKET_TIMEOUT': 5
}
ES_CONFIG = {
    'HOST': 'http://localhost:9200',
    'INDEX_NAME': 'questions',
    'TIMEOUT': 30
}
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

FIELD_MAPPINGS = {'题目编号': 'question_id', '题目': 'content', '题目内容': 'content', '题型': 'question_type',
                  '难度': 'difficulty', '答案': 'answer', '选项A': 'options.0.text', '选项A图片': 'options.0.image',
                  '选项B': 'options.1.text', '选项B图片': 'options.1.image', '选项C': 'options.2.text',
                  '选项C图片': 'options.2.image','选项D': 'options.3.text','选项D图片': 'options.3.image' }
ALLOWED_FIELDS = list(FIELD_MAPPINGS.values()) + [
    'explanation',
    'source',
    'ingest_time'
]
