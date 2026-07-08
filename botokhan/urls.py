from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django's built-in admin — optional, useful for a superuser/developer.
    # The store's own admin interface lives under /admin-panel/ (see store/urls.py).
    path('django-admin/', admin.site.urls),

    path('', include('store.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Static files (CSS/JS/images under store/static/) are served automatically
    # by `runserver` in development because 'django.contrib.staticfiles' is
    # installed — no extra config needed here.
