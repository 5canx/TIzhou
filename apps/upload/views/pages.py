"""
上传页面视图
"""
from django.shortcuts import render


def upload_page(request):
    """文件上传页面"""
    return render(request, 'upload/upload.html')


def upload_images_page(request):
    """图片上传页面"""
    return render(request, 'upload/upload_images.html') 