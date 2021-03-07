from django.urls import path, include
from api.routers import router

urlpatterns = [
    path("", include(router.urls)),
]
