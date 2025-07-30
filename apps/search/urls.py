from django.urls import path
from .views import search_by_id, search_by_content, list_all_questions

app_name = 'search'

urlpatterns = [
    path('id/', search_by_id, name='search_by_id'),
    path('content/', search_by_content, name='search_by_content'),
    path('all/', list_all_questions, name='list_all_questions'),
] 