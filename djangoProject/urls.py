from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from index.views.search import search_by_id, search_by_content, list_all_questions
from index.views.upload import upload_file, upload_images
from index.views.pages import upload, search, custom_404_view,upload_images_page
from index.admin import custom_admin_site

handler404 = custom_404_view

urlpatterns = [
    path("api/search/id/", search_by_id, name="search_by_id"),
    path("api/search/content/", search_by_content, name="search_by_content"),
    path("api/search/all/", list_all_questions, name="list_all_questions"),
    path('admin/', custom_admin_site.urls),
    path("api/upload/file/", upload_file, name="upload_file"),
    path("upload/file/", upload_file, name="upload_file"),
    path("upload/", upload, name="upload"),
    path("search/", search, name="search"),
    path("upload/images/page/", upload_images_page, name="upload_images_page"),  # ✅ 渲染上传页面
    path("upload/images/", upload_images, name="upload_images"),  # ✅ 上传 zip 的 API
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
