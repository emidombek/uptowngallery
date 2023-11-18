from django.shortcuts import render, redirect
from django.views import View
from .models import Artwork, Category, Auction
from .forms import ArtworkCreateForm


class LandingPageView(View):
    def get(self, request):
        top_categories = Category.objects.all()[:9]
        recent_artworks = Artwork.objects.filter(
            approved=True
        ).order_by("-create_date")[:10]
        return render(
            request,
            "index.html",
            {
                "top_categories": top_categories,
                "recent_artworks": recent_artworks,
            },
        )


class ArtworkListView(View):
    def get(self, request):
        artworks = Artwork.objects.all()
        return render(
            request, "artwork_list.html", {"artworks": artworks}
        )


class CreateArtworkView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            # Redirect to the sign-in page if the user is not authenticated
            return redirect("signin_page")

        form = ArtworkCreateForm()
        return render(request, "create_artwork.html", {"form": form})

    def post(self, request):
        if not request.user.is_authenticated:
            # Redirect to the sign-in page if the user is not authenticated
            return redirect("signin_page")

        form = ArtworkCreateForm(request.POST, request.FILES)
        if form.is_valid():
            artwork = form.save(commit=False)
            artwork.artist = (
                request.user.profile
            )  # Assuming I have a UserProfile for each user
            artwork.save()
            return redirect("artwork_detail", artwork.id)
        return render(request, "create_artwork.html", {"form": form})


class PendingArtworksView(View):
    def get(self, request):
        artworks = Artwork.objects.filter(approved=False)
        return render(
            request, "pending_artworks.html", {"artworks": artworks}
        )


class ApproveArtworkView(View):
    def get(self, request, artwork_id):
        artwork = Artwork.objects.get(pk=artwork_id)
        artwork.approved = True
        artwork.save()
        return redirect("start_auction", artwork_id)


class StartAuctionView(View):
    def get(self, request, artwork_id):
        artwork = Artwork.objects.get(pk=artwork_id)
        auction = Auction.objects.create(
            artwork=artwork, status="active"
        )
        return redirect("auction_detail", auction.id)
