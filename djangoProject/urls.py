from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from apps.core.admin import custom_admin_site
from apps.questions.views import custom_404_view

handler404 = custom_404_view

urlpatterns = [
    path('admin/', custom_admin_site.urls),
    path('users/', include('apps.users.urls')),
    path('moderator/', include('apps.moderator.urls')),
    path('api/search/', include('apps.search.urls')),
    path('api/upload/', include('apps.upload.urls')),
    path('search/', include('apps.questions.urls')),
    path('upload/', include('apps.upload.urls')),
    path('', lambda request: redirect('users:login'), name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
