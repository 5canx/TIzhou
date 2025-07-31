from django.urls import path

from .views.pages import upload_images_page
from .views import upload_page
from .views.api import upload_file_view, upload_images_view
app_name = 'upload'

urlpatterns = [
    # API路由
    path('file/', upload_file_view, name='upload_file'),
    path('images/', upload_images_view, name='upload_images'),
    
    # 页面路由
    path('', upload_page, name='upload_page'),
    path('images/page/', upload_images_page, name='upload_images_page'),
] 