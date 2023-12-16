import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Max, Prefetch
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import (
    Artwork,
    Category,
    Auction,
    Bids,
)
from .forms import ArtworkCreateForm
from .forms import CustomSignupForm


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
        # Fetch artworks that have at least one active auction
        artworks = Artwork.objects.filter(
            approval_status="approved",
            auctions__status="active",  # Ensure the artwork has active auctions
        ).distinct()  # Use distinct to avoid duplicate artworks

        # Annotate each artwork with the ID of its most recent active auction
        artworks = artworks.annotate(
            recent_auction_id=Max(
                "auctions__id", filter=Q(auctions__status="active")
            )
        )

        # Prefetch the related recent active auction for each artwork
        artworks = artworks.prefetch_related(
            Prefetch(
                "auctions",
                queryset=Auction.objects.filter(
                    id__in=[
                        artwork.recent_auction_id
                        for artwork in artworks
                    ],
                    status="active",  # Fetch only active auctions
                ),
                to_attr="recent_auction",
            )
        )

        # ... (rest of your pagination logic) ...

        return render(
            request, "artwork_list.html", {"artworks": artworks}
        )


class CreateArtworkView(LoginRequiredMixin, CreateView):
    template_name = "create_artwork.html"
    form_class = ArtworkCreateForm
    success_url = reverse_lazy("pending_artworks")

    def form_valid(self, form):
        form.instance.artist = self.request.user.profile
        # Set initial auction-related fields in the Artwork instance
        form.instance.auction_start = (
            None  # Auction will start upon approval
        )
        form.instance.approval_status = "pending"  # Initial status
        # Save the Artwork instance
        return super().form_valid(form)

    def form_invalid(self, form):
        print("Form is invalid")
        print(form.errors)  # Print the form errors
        messages.error(
            self.request,
            "Artwork creation failed. Please check the form.",
        )
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print("Context data:", context)
        return context

    def post(self, request, *args, **kwargs):
        print("POST request data:", request.POST)
        return super().post(request, *args, **kwargs)


class PendingArtworksView(View):
    def get(self, request):
        # Filter artworks to show only pending artworks of the current user
        artworks = Artwork.objects.filter(
            artist=request.user.profile, approved=False
        )

        # Paginate the artworks
        paginator = Paginator(artworks, 10)  # Show 10 artworks per page
        page = request.GET.get("page")

        try:
            artworks = paginator.page(page)
        except PageNotAnInteger:
            artworks = paginator.page(1)
        except EmptyPage:
            artworks = paginator.page(paginator.num_pages)

        return render(
            request, "pending_artworks.html", {"artworks": artworks}
        )


class ApproveArtworkView(View):
    def get(self, request, artwork_id):
        artwork = get_object_or_404(Artwork, pk=artwork_id)

        if (
            artwork.approval_status == "pending"
            and request.user.is_staff
        ):

            def on_approval_commit():
                artwork.approve_and_start_auction()

            with transaction.atomic():
                artwork.approval_status = "approved"
                artwork.save()
                transaction.on_commit(on_approval_commit)

            messages.success(
                request,
                f"The artwork '{artwork.title}' has been approved, and the auction started.",
            )
        else:
            messages.error(
                request,
                f"The artwork '{artwork.title}' cannot be approved. Check if it's pending approval or if I have the right permissions.",
            )

        return redirect("artwork_detail", artwork_id)


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


class AuctionDetailView(View):
    def get(self, request, artwork_id, auction_id):
        artwork = get_object_or_404(Artwork, pk=artwork_id)
        auction = get_object_or_404(
            Auction, pk=auction_id, artwork=artwork
        )
        latest_bid = auction.bids.order_by("-amount").first()

        context = {
            "auction": auction,
            "artwork": artwork,
            "latest_bid": latest_bid,
        }
        return render(request, "auction_detail.html", context)


class ProfileInfoView(View):
    template_name = "profile_info.html"

    def get_context_data(self, **kwargs):
        context = {}

        # Add Ir logic to fetch the winning bid amount here
        user_profile = self.request.user.profile
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


class PlaceBidView(CreateView):
    model = Bids
    template_name = "place_bid.html"
    fields = ["amount"]
    success_url = reverse_lazy(
        "auction_list"
    )  # Redirect to the auction list after successful bid

    def form_valid(self, form):
        # Retrieve auction and other necessary data
        auction_id = self.kwargs["auction_id"]
        auction = Auction.objects.get(pk=auction_id)

        # Get bid amount from the form
        bid_amount = form.cleaned_data["amount"]

        # Validate bid amount against the reserve price
        if bid_amount < auction.reserve_price:
            messages.error(
                self.request,
                "Bid amount cannot be lower than the reserve price.",
            )
            return self.form_invalid(form)

        # Check if the bid is higher than the current highest bid (if any)
        current_highest_bid = auction.bids.order_by("-amount").first()

        if (
            current_highest_bid is None
            or bid_amount > current_highest_bid.amount
        ):
            # Proceed with creating the bid
            form.instance.bidder = self.request.user.profile
            form.instance.auction = auction
            form.instance.amount = bid_amount
            messages.success(self.request, "Bid placed successfully!")
            return super().form_valid(form)
        else:
            messages.error(
                self.request,
                "Ir bid is not higher than the current highest bid.",
            )
            return self.form_invalid(form)
