from django.urls import path
from .views import upload_file, upload_images, upload_page, upload_images_page

app_name = 'upload'

urlpatterns = [
    # API路由
    path('file/', upload_file, name='upload_file'),
    path('images/', upload_images, name='upload_images'),
    
    # 页面路由
    path('', upload_page, name='upload_page'),
    path('images/page/', upload_images_page, name='upload_images_page'),
] 