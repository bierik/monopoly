from django.urls import path, re_path, include
from django.contrib import admin
from django.views.generic import TemplateView

admin.autodiscover()

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    re_path(r"", TemplateView.as_view(template_name="index.html")),
]
