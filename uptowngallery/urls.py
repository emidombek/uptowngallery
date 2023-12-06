# uptown_gallery/urls.py
from django.urls import path
from .views import (
    LandingPageView,
    ArtworkListView,
    CreateArtworkView,
    PendingArtworksView,
    ApproveArtworkView,
    StartAuctionView,
    ProfileInfoView,
    signup_view,
)

urlpatterns = [
    path("", LandingPageView.as_view(), name="home"),
    path("artworks/", ArtworkListView.as_view(), name="artwork_list"),
    path("create/", CreateArtworkView.as_view(), name="create_artwork"),
    path(
        "admin/pending/",
        PendingArtworksView.as_view(),
        name="pending_artworks",
    ),
    path(
        "admin/approve/<int:artwork_id>/",
        ApproveArtworkView.as_view(),
        name="approve_artwork",
    ),
    path(
        "admin/start-auction/<int:artwork_id>/",
        StartAuctionView.as_view(),
        name="start_auction",
    ),
    path("signup/", signup_view, name="account_signup"),
    path("profile/", ProfileInfoView.as_view(), name="profile_info"),
]
