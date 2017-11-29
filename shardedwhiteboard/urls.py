from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from BoardApp.views import *

# rest
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"report", ReportViewSet)
router.register(r"board", BoardViewSet)

urlpatterns = [
    url(r"^$", Index),
    url(r"^admin/", admin.site.urls),
    url(r"^draw/([a-zA-Z0-9]{6})", Draw),
    url(r"^api/", include(router.urls)),
    # url(r"^api-auth/", include('rest_framework.urls', namespace='rest_framework')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
