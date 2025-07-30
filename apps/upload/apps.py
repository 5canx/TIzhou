from django.apps import AppConfig


class UploadConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.upload'
    verbose_name = '文件上传' 