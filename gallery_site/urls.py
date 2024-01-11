from django.contrib import admin
from django.urls import path, include
from django.conf import settings


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("uptowngallery.urls"), name="uptowngallery_urls"),
    path("accounts/", include("allauth.urls")),
]

handler404 = "uptowngallery.views.handler404"
handler500 = "uptowngallery.views.handler500"
