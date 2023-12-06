import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import (
    Artwork,
    Category,
    Auction,
    UserProfile,
    Bids,
)
from .forms import ArtworkCreateForm
from .forms import CustomSignupForm
from django.utils.decorators import method_decorator
from django.db.models import F

logger = logging.getLogger(__name__)


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
        # Number of artworks to display per page
        items_per_page = 12

        # Create a Paginator object
        paginator = Paginator(artworks, items_per_page)

        # Get the current page number from the request's GET parameters
        page = request.GET.get("page")

        try:
            # Get the Page object for the requested page
            artworks = paginator.page(page)
        except PageNotAnInteger:
            # If the page parameter is not an integer, display the first page
            artworks = paginator.page(1)
        except EmptyPage:
            # If the page is out of range (e.g., 9999), deliver the last page of results
            artworks = paginator.page(paginator.num_pages)

        return render(
            request, "artwork_list.html", {"artworks": artworks}
        )


class CreateArtworkView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            # Redirect to the sign-in page if the user is not authenticated
            return redirect("account_login")

        form = ArtworkCreateForm()
        return render(request, "create_artwork.html", {"form": form})

    def post(self, request):
        if not request.user.is_authenticated:
            # Redirect to the sign-in page if the user is not authenticated
            return redirect("account_login")

        form = ArtworkCreateForm(request.POST, request.FILES)
        if form.is_valid():
            artwork = form.save(
                commit=False, user_profile=request.user.profile
            )
            artwork.artist = request.user.profile

            # Save the artwork with auction duration
            artwork.save()

            # Get the selected auction duration
            duration = int(form.cleaned_data.get("auction_duration"))

            # Start an auction for the artwork with the selected duration
            auction = Auction.objects.create(
                artwork=artwork, status="active", duration=duration
            )

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

        # Start the auction for the approved artwork
        auction = Auction.objects.create(
            artwork=artwork,
            status="active",
            duration=artwork.auction_duration,
        )

        messages.success(
            request,
            f"The artwork '{artwork.title}' has been approved and the auction started.",
        )
        return redirect("artwork_detail", artwork_id)


class StartAuctionView(View):
    def get(self, request, artwork_id):
        artwork = Artwork.objects.get(pk=artwork_id)
        auction = Auction.objects.create(
            artwork=artwork, status="active"
        )
        return redirect("auction_detail", auction.id)


def signup_view(request):
    logger.info("Entering signup_view function")

    if request.method == "POST":
        form = CustomSignupForm(request.POST)
        logger.info(f"Form data: {form.data}")
        logger.info(f"Form is valid: {form.is_valid()}")

        if form.is_valid():
            logger.info("Form is valid. Proceeding to save.")
            user = form.save(request)
            logger.info(f"User saved: {user}")
            return redirect("verification_sent")
    else:
        form = CustomSignupForm()

    logger.info("Rendering signup template.")
    return render(request, "signup_template.html", {"form": form})


@method_decorator(login_required, name="dispatch")
class ProfileInfoView(View):
    template_name = "profile_info.html"

    def get_context_data(self, **kwargs):
        context = {}

        # Add Ir logic to fetch the winning bid amount here
        user_profile = (
            self.request.user.profile
        )  # Assuming I have a one-to-one relationship between User and Profile
        winning_bid = (
            Bids.objects.filter(
                bidder=user_profile, auction__artwork__approved=True
            )
            .order_by("-amount")
            .first()
        )

        if winning_bid:
            winning_bid_amount = winning_bid.amount
        else:
            winning_bid_amount = None

        # Add other context data as needed
        context["winning_bid_amount"] = winning_bid_amount
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)
