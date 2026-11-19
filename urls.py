from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.public import views as public_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', public_views.home, name='home'),
    path('auth/', include('apps.accounts.urls')),
    path('dashboard/', include('apps.resumes.urls')),
    path('analysis/', include('apps.analysis.urls')),
    path('jd-match/', include('apps.jd_match.urls')),
    path('improvement/', include('apps.improvement.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('feedback/', include('apps.feedback.urls')),
    path('admin-panel/', include('apps.portal_admin.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
