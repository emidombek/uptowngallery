import logging
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.middleware.csrf import get_token
from django.db.models import Q, Max, Prefetch
from django.views import View
from django.views.generic import TemplateView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.utils import timezone
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
        category = request.GET.get(
            "category"
        )  # Get the category from the request

        artworks = Artwork.objects.filter(
            approval_status="approved", auctions__status="active"
        ).distinct()

        artworks = artworks.order_by("-create_date")

        # Filter by category if it's provided
        if category:
            artworks = artworks.filter(category=category)

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

        # Implement Pagination
        paginator = Paginator(artworks, 10)  # Show 10 artworks per page
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        return render(
            request, "artwork_list.html", {"page_obj": page_obj}
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


class RejectArtworkView(View):
    def get(self, request, artwork_id):
        artwork = get_object_or_404(Artwork, pk=artwork_id)

        if (
            artwork.approval_status == "pending"
            and request.user.is_staff
        ):
            artwork.approval_status = "rejected"
            artwork.save()

            # Update any related auctions, if necessary
            Auction.objects.filter(artwork=artwork).update(
                status="cancelled", is_active=False
            )

            messages.success(
                request,
                f"The artwork '{artwork.title}' has been rejected.",
            )
        else:
            messages.error(
                request,
                f"The artwork '{artwork.title}' cannot be rejected. Check if it's pending approval or if I have the right permissions.",
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

        # Calculate the current price
        bids = Bids.objects.filter(auction=auction).order_by("-amount")
        current_price = (
            bids.first().amount
            if bids.exists()
            else auction.reserve_price
        )

        context = {
            "auction": auction,
            "artwork": artwork,
            "current_price": current_price,  # Pass current price to the template
        }

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            # Return the partial template for AJAX requests
            return render(
                request, "auction_detail_partial.html", context
            )
        else:
            # Return the full page for regular requests
            return render(request, "auction_detail.html", context)

    def post(self, request, artwork_id, auction_id):
        artwork = get_object_or_404(Artwork, pk=artwork_id)
        auction = get_object_or_404(
            Auction, pk=auction_id, artwork=artwork
        )

        try:
            bid_amount = int(request.POST.get("bid_amount"))

            if bid_amount <= auction.reserve_price:
                messages.error(
                    request,
                    "Bid amount must be higher than the reserve price.",
                )
                return redirect(
                    "auction_detail",
                    artwork_id=artwork_id,
                    auction_id=auction_id,
                )

            # Assuming bid amount is valid and higher than current highest bid
            Bids.objects.create(
                bidder=request.user.profile,
                auction=auction,
                amount=bid_amount,
                bid_time=timezone.now(),
            )
            messages.success(
                request, "My bid was submitted successfully!"
            )

        except ValueError:
            # Handle the case where bid_amount is not a valid integer
            messages.error(request, "Invalid bid amount.")
            return redirect(
                "auction_detail",
                artwork_id=artwork_id,
                auction_id=auction_id,
            )

        # Redirect back to the auction detail page or to any specific page I want after successful bid submission
        return redirect(
            "auction_detail",
            artwork_id=artwork_id,
            auction_id=auction_id,
        )
        # Or redirect to art_list or any other page I prefer
        # return redirect("art_list")


class ProfileInfoView(LoginRequiredMixin, View):
    template_name = "profile_info.html"

    def get(self, request, *args, **kwargs):
        user_profile = request.user.profile
        winning_bid = (
            Bids.objects.filter(
                bidder=user_profile, auction__artwork__approved=True
            )
            .order_by("-amount")
            .first()
        )

        context = {
            "profile": user_profile,
            "winning_bid_amount": winning_bid.amount
            if winning_bid
            else None,
            "csrf_token": get_token(
                request
            ),  # Retrieves the CSRF token
        }

        return render(request, self.template_name, context)


class UpdateProfileView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        field = request.POST.get("field")
        value = request.POST.get("value")
        user_profile = request.user.profile

        # Define a mapping of field names to model fields
        field_mapping = {
            "name": "name",
            "shipping_address": "shipping_address",  # Backend field name
        }

        if field in field_mapping:
            setattr(user_profile, field_mapping[field], value)
            user_profile.save()
            return JsonResponse(
                {
                    "status": "success",
                    "field": field,
                    "new_value": value,
                }
            )
        else:
            return JsonResponse(
                {"status": "error", "message": "Invalid field"},
                status=400,
            )


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


class ActivityDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        user_profile = (
            request.user.profile
        )  # Retrieve the UserProfile instance

        # Fetch bidding activity
        bidding_activity = Bids.objects.filter(
            bidder=user_profile
        ).select_related("auction")

        # Fetch selling activity
        selling_activity = Artwork.objects.filter(artist=user_profile)

        # Fetch active auctions
        active_auctions = Auction.objects.filter(
            artwork__artist=user_profile,
            status="active",
            artwork__approval_status="approved",
        )

        # Fetch closed auctions and enhance with final price
        closed_auctions = Auction.objects.filter(
            artwork__artist=user_profile, status="closed"
        ).select_related("artwork")
        for auction in closed_auctions:
            final_bid = (
                Bids.objects.filter(auction=auction)
                .order_by("-amount")
                .first()
            )
            auction.final_price = (
                final_bid.amount if final_bid else auction.reserve_price
            )

        # Consolidate all context data
        context = {
            "bidding_activity": bidding_activity,
            "selling_activity": selling_activity,
            "active_auctions": active_auctions,
            "closed_auctions": closed_auctions,
        }

        return render(request, "activity.html", context)


class AboutView(TemplateView):
    template_name = "about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
