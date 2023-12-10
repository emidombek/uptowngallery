import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .models import (
    Artwork,
    Category,
    Auction,
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


class CreateArtworkView(LoginRequiredMixin, CreateView):
    template_name = "create_artwork.html"
    form_class = ArtworkCreateForm
    success_url = reverse_lazy("artwork_list")

    def form_valid(self, form):
        form.instance.artist = self.request.user.profile
        response = super().form_valid(form)

        # Additional processing after form validation
        duration = form.cleaned_data.get("auction_duration")
        Auction.objects.create(artwork=self.object, status="pending")

        return response

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
        artwork = Artwork.objects.get(pk=artwork_id)

        # Check if the artwork is pending approval
        if artwork.approval_status == "pending":
            # Additional admin-specific check
            if request.user.is_staff:
                artwork.approve_and_start_auction()
                messages.success(
                    request,
                    f"The artwork '{artwork.title}' has been approved, and the auction started.",
                )
            else:
                # Handle non-admin case, e.g., redirect to access denied page
                messages.error(
                    request,
                    f"Only admins can approve artworks.",
                )
        else:
            messages.error(
                request,
                f"The artwork '{artwork.title}' is not pending approval.",
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


@method_decorator(login_required, name="dispatch")
class AuctionDetailView(View):
    def get(self, request, auction_id):
        auction = Auction.objects.get(pk=auction_id)

        # Ensure that the auction is active
        if auction.status == "active":
            # I may want to fetch related information and pass it to the template
            return render(
                request, "auction_detail.html", {"auction": auction}
            )
        else:
            messages.error(request, "This auction is not active.")
            return redirect("some_redirect_view")


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
