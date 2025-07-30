from django.apps import AppConfig


class ModeratorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.moderator'
    verbose_name = '题目审核' 