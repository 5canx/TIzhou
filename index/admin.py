from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.template.response import TemplateResponse
from index.views.utils import es, index_name  # 你调用ES搜索的代码

class CustomAdminSite(admin.AdminSite):
    site_header = "我的后台"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('es_questions/', self.admin_view(self.es_questions_view), name='es_questions'),
        ]
        return custom_urls + urls

    def es_questions_view(request):
        return render(request, 'admin/es_questions.html')

custom_admin_site = CustomAdminSite(name='custom_admin')
