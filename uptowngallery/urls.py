# uptown_gallery/urls.py
from django.urls import path
from .views import (
    LandingPageView,
    ArtworkListView,
    CreateArtworkView,
    PendingArtworksView,
    ApproveArtworkView,
    AuctionDetailView,
    ProfileInfoView,
    signup_view,
)

urlpatterns = [
    path("", LandingPageView.as_view(), name="home"),
    path("artworks/", ArtworkListView.as_view(), name="artwork_list"),
    path("create/", CreateArtworkView.as_view(), name="create_artwork"),
    path(
        "pending_artworks/",
        PendingArtworksView.as_view(),
        name="pending_artworks",
    ),
    path(
        "admin/approve/<int:artwork_id>/",
        ApproveArtworkView.as_view(),
        name="approve_artwork",
    ),
    path(
        "auction_detail/<int:auction_id>/",
        AuctionDetailView.as_view(),
        name="auction_detail",
    ),
    path("signup/", signup_view, name="account_signup"),
    path("profile/", ProfileInfoView.as_view(), name="profile_info"),
]
