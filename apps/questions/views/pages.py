"""
题目页面视图
"""
from django.shortcuts import render


def search_page(request):
    """搜索页面"""
    return render(request, 'questions/search.html')


def custom_404_view(request, exception):
    """404页面"""
    return render(request, '404.html', status=404) 