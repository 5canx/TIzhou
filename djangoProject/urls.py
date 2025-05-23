from django.urls import path
from index.views.search import search_by_id, search_by_content, list_all_questions
from index.views.upload import upload_file
from index.views.pages import upload, search
from index.admin import custom_admin_site
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path("api/search/id/", search_by_id, name="search_by_id"),
    path("api/search/content/", search_by_content, name="search_by_content"),
    path("api/search/all/", list_all_questions, name="list_all_questions"),
    path('admin/', custom_admin_site.urls),  # 包含 es_questions 路由
    path("api/upload/file/", upload_file, name="upload_file"),
    path("upload/", upload, name="upload"),
    path("search/", search, name="search"),
]