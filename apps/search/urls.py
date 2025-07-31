from django.urls import path
from .views import api

urlpatterns = [
    path('id/', api.search_by_id, name='search_by_id'),
    path('content/', api.search_by_content, name='search_by_content'),
    path('list/', api.list_all_questions, name='list_all_questions'),
]