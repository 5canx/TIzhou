from django.urls import path
from index.views.search import search_by_id, search_by_content, list_all_questions
from index.views.upload import upload_file
from index.views.pages import upload, search, custom_404_view
from index.admin import custom_admin_site

# 这是Django识别自定义404的关键配置
handler404 = custom_404_view  # 直接引用视图函数

urlpatterns = [
    path("api/search/id/", search_by_id, name="search_by_id"),
    path("api/search/content/", search_by_content, name="search_by_content"),
    path("api/search/all/", list_all_questions, name="list_all_questions"),
    path('admin/', custom_admin_site.urls),
    path("api/upload/file/", upload_file, name="upload_file"),
    path("upload/", upload, name="upload"),
    path("search/", search, name="search"),
]