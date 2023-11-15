from . import views
from django.urls import path

urlpatterns = [
    path("", views.LandingPageView.as_view(), name="home"),
]
