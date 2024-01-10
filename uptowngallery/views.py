from django.db import transaction
from django.db.models import Q, Max, Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.middleware.csrf import get_token
from .forms import ArtworkCreateForm, CustomSignupForm, BidForm
from .models import Artwork, Auction, Bids
from .signals import bid_placed, profile_updated


class LandingPageView(View):
    """
    Retrieve 10 most recent artowrks to display
    """

    def get(self, request):
        recent_artworks = Artwork.objects.filter(
            approved=True
        ).order_by("-create_date")[:10]
        return render(
            request,
            "index.html",
            {
                "recent_artworks": recent_artworks,
            },
        )


class ArtworkListView(View):
    """
    Gets the category from the request
    Filters by category
    Annotate each artwork with the ID of its most recent active auction
    Prefetch the related recent active auction for each artwork
    Implement Pagination,show 10 artworks per page
    Pass the category to the template
    """

    def get(self, request):
        category = request.GET.get("category")
        artworks = Artwork.objects.filter(
            approval_status="approved", auctions__status="active"
        ).distinct()
        artworks = artworks.order_by("-create_date")
        if category:
            artworks = artworks.filter(category=category)
        artworks = artworks.annotate(
            recent_auction_id=Max(
                "auctions__id", filter=Q(auctions__status="active")
            )
        )
        artworks = artworks.prefetch_related(
            Prefetch(
                "auctions",
                queryset=Auction.objects.filter(
                    id__in=[
                        artwork.recent_auction_id
                        for artwork in artworks
                    ],
                    status="active",
                ),
                to_attr="recent_auction",
            )
        )
        paginator = Paginator(artworks, 10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        return render(
            request,
            "artwork_list.html",
            {
                "page_obj": page_obj,
                "category": category,
            },
        )


class CreateArtworkView(LoginRequiredMixin, CreateView):
    """
    Sets form class and template name
    Redirects to pending artworks page if successful
    Set initial auction-related fields in the Artwork instance to None,
    sets user as artist
    Set the 'approval_status' attribute of the form's instance to "pending"
    Call the parent class's `form_valid` method to continue processing the form submission if form is valid
    Save the form's instance to the database
    Prints errors if form is not valid
    Logging the context data and returning it without modifications
    Logging the POST data and then calling the parent class's post method to handle the form submission
    """

    template_name = "create_artwork.html"
    form_class = ArtworkCreateForm
    success_url = reverse_lazy("pending_artworks")

    def form_valid(self, form):
        form.instance.artist = self.request.user.profile
        form.instance.auction_start = None
        form.instance.approval_status = "pending"
        return super().form_valid(form)

    def form_invalid(self, form):
        print("Form is invalid")
        print(form.errors)
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


class PendingArtworksView(LoginRequiredMixin, View):
    """
    Filter artworks to show only pending artworks of the current user
    Paginate the artworks,
    show 10 artworks per page
    """

    def get(self, request):
        artworks = Artwork.objects.filter(
            artist=request.user.profile, approved=False
        )
        paginator = Paginator(artworks, 10)
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

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        artwork_id = request.POST.get("artwork_id")
        artwork = get_object_or_404(
            Artwork, id=artwork_id, artist=request.user.profile
        )
        if action == "delete":
            artwork.delete()
            messages.success(request, "Artwork deleted successfully.")
            return redirect("pending_artworks")
        elif action == "update":
            form = ArtworkCreateForm(
                request.POST, request.FILES, instance=artwork
            )
            if form.is_valid():
                form.save()
                messages.success(
                    request, "Artwork updated successfully."
                )
                return redirect("pending_artworks")
            else:
                pass
                return redirect("pending_artworks")


def signup_view(request):
    """
    View that sets a custom sign up form,
    validate and save.
    """
    if request.method == "POST":
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            user = form.save(request)
            return redirect("verification_sent")
    else:
        form = CustomSignupForm()
    return render(request, "account/signup.html", {"form": form})


class AuctionDetailView(LoginRequiredMixin, View):
    """
    Fetch artwork and auction or return 404 if not found
    Get all bids for the auction,
    calculate current highest bid or use reserve price
    Prepare context and render appropriate template based on request type (AJAX or regular)
    Fetch artwork and auction for bid processing
    Process bid form
    Save bid data, send signal, and redirect on successful bid
    Add form errors as messages and redisplay form with errors
    """

    def get(self, request, artwork_id, auction_id):
        artwork = get_object_or_404(Artwork, pk=artwork_id)
        auction = get_object_or_404(
            Auction, pk=auction_id, artwork=artwork
        )
        bids = Bids.objects.filter(auction=auction).order_by("-amount")
        current_price = (
            bids.first().amount
            if bids.exists()
            else auction.reserve_price
        )
        form = BidForm()
        context = {
            "auction": auction,
            "artwork": artwork,
            "current_price": current_price,
            "form": form,
        }
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return render(
                request, "auction_detail_partial.html", context
            )
        else:
            return render(request, "auction_detail.html", context)

    def post(self, request, artwork_id, auction_id):
        artwork = get_object_or_404(Artwork, pk=artwork_id)
        auction = get_object_or_404(
            Auction, pk=auction_id, artwork=artwork
        )
        form = BidForm(request.POST, auction=auction)
        if form.is_valid():
            bid = form.save(commit=False)
            bid.bidder = request.user.profile
            bid.auction = auction
            bid.bid_time = timezone.now()
            bid.save()
            bid_placed.send(
                sender=self.__class__, bid=bid, user=request.user
            )
            messages.success(
                request, "Your bid was submitted successfully!"
            )
            return redirect(
                "auction_detail",
                artwork_id=artwork_id,
                auction_id=auction_id,
            )
        else:
            for error in form.errors.values():
                messages.error(request, error)
            return self.get(request, artwork_id, auction_id)


class ProfileInfoView(LoginRequiredMixin, View):
    """
    Get template and profile info
    """

    template_name = "profile_info.html"

    def get(self, request, *args, **kwargs):
        user_profile = request.user.profile

        context = {
            "profile": user_profile,
            "csrf_token": get_token(request),
        }
        return render(request, self.template_name, context)


class UpdateProfileView(LoginRequiredMixin, View):
    """
    A view to update user profile fields. It accepts POST requests to update specific fields
    of the user's profile based on a predefined field mapping.
    Extract the field name and its new value from the POST request.
    Retrieve the current user's profile.
    Define a mapping between the field names accepted in the request and the actual
    Check if the requested field is in the field mapping.
    Update the specified field with the new value.
    Send a signal indicating that the profile has been updated.
    Return a success response as JSON.
    If the field is not in the mapping, return an error response.
    """

    def post(self, request, *args, **kwargs):
        field = request.POST.get("field")
        value = request.POST.get("value")
        user_profile = request.user.profile
        field_mapping = {
            "name": "name",
            "shipping_address": "shipping_address",
        }
        if field in field_mapping:
            setattr(user_profile, field_mapping[field], value)
            user_profile.save()
            profile_updated.send(
                sender=self.__class__,
                user=request.user,
                field=field,
                new_value=value,
            )
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


class UpdatePendingArtworkView(LoginRequiredMixin, View):
    """
    A view to update user profile fields. It accepts POST requests to update specific fields
    of the user's profile based on a predefined field mapping.
    Extract the field name and its new value from the POST request.
    Retrieve the current user's profile.
    Define a mapping between the field names accepted in the request and the actual
    Check if the requested field is in the field mapping.
    Update the specified field with the new value.
    Send a signal indicating that the profile has been updated.
    Return a success response as JSON.
    If the field is not in the mapping, return an error response.
    """

    def post(self, request, *args, **kwargs):
        field = request.POST.get("field")
        value = request.POST.get("value")
        user_profile = request.user.profile
        field_mapping = {
            "name": "name",
            "shipping_address": "shipping_address",
        }
        if field in field_mapping:
            setattr(user_profile, field_mapping[field], value)
            user_profile.save()
            profile_updated.send(
                sender=self.__class__,
                user=request.user,
                field=field,
                new_value=value,
            )
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


class UpdatePendingArtworkView(LoginRequiredMixin, View):
    """
    A view to update fields of an artwork. It accepts POST requests to update specific fields
    of an artwork based on the artwork's ID and a predefined field mapping.
    Extract the artwork ID, field name, and its new value from the POST request.
    Retrieve the specified artwork.
    Define a mapping between the field names accepted in the request and the actual
    model fields.
    Check if the requested field is in the field mapping and if the user has permission
    to update the artwork.
    Update the specified field with the new value.
    Return a success response as JSON.
    If the field is not in the mapping or the artwork doesn't belong to the user, return an error response.
    """

    def post(self, request, *args, **kwargs):
        artwork_id = request.POST.get("artwork_id")
        field = request.POST.get("field")
        value = request.POST.get("value")

        artwork = get_object_or_404(
            Artwork, id=artwork_id, artist=request.user.profile
        )

        field_mapping = {
            "title": "title",
            "description": "description",
        }

        if field in field_mapping:
            setattr(artwork, field_mapping[field], value)
            artwork.save()
            return JsonResponse(
                {
                    "status": "success",
                    "field": field,
                    "new_value": value,
                }
            )

        else:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Invalid field or unauthorized access",
                },
                status=400,
            )


class ActivityDashboardView(LoginRequiredMixin, View):
    """
    View for displaying and managing user's activity dashboard. It handles showing the user's bidding and selling
    activities, their active and closed auctions, and allows for deletion of closed auctions.
    Retrieve the UserProfile instance
    Fetch bidding activity
    Fetch selling activity
    Fetch active auctions
    Fetch closed auctions and enhance with final price
    Consolidate all context data
    """

    def get(self, request):
        """
        Handles GET requests. Fetches and displays the user's bidding activity, selling activity, active auctions,
        and closed auctions with final prices.
        """
        user_profile = request.user.profile
        bidding_activity = Bids.objects.filter(
            bidder=user_profile
        ).select_related("auction")
        selling_activity = Artwork.objects.filter(artist=user_profile)
        active_auctions = Auction.objects.filter(
            artwork__artist=user_profile,
            status="active",
            artwork__approval_status="approved",
        )
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
        context = {
            "bidding_activity": bidding_activity,
            "selling_activity": selling_activity,
            "active_auctions": active_auctions,
            "closed_auctions": closed_auctions,
        }
        return render(request, "activity.html", context)

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests. Used for deleting closed auctions that belong to the user. Validates auction status
        before deletion and provides appropriate success or error messages.
        """
        auction_id = request.POST.get("auction_id")

        if auction_id:
            auction = get_object_or_404(
                Auction,
                pk=auction_id,
                artwork__artist=request.user.profile,
            )

            if auction.status == "closed":
                auction.delete()
                messages.success(
                    request, "Auction deleted successfully."
                )
            else:
                messages.error(
                    request, "Cannot delete active auctions."
                )
        else:
            messages.error(request, "Invalid auction ID.")

        return redirect("activity.html")


class AboutView(TemplateView):
    template_name = "about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)


class SearchActiveAuctionArtworkView(View):
    """
    A view to handle searching for artworks in active auctions. It accepts a search query and
    returns artworks that match the query criteria (title, approval status, and active auction status).
    """

    def get(self, request):
        """
        Processes GET requests to perform a search based on a query string. It filters artworks by title,
        ensuring they are approved and part of active auctions. The view supports pagination and shows the results
        on an artwork list page.
        """
        query = request.GET.get("query", "").strip()

        context = {
            "is_search": True,
            "query": query,
        }
        if query:
            artworks = (
                Artwork.objects.filter(
                    title__icontains=query,
                    approval_status="approved",
                    auctions__status="active",
                )
                .distinct()
                .order_by("-create_date")
            )
            artworks = artworks.annotate(
                recent_auction_id=Max(
                    "auctions__id", filter=Q(auctions__status="active")
                )
            )
            recent_auction_ids = list(
                filter(
                    None,
                    artworks.values_list(
                        "recent_auction_id", flat=True
                    ),
                )
            )
            artworks = artworks.prefetch_related(
                Prefetch(
                    "auctions",
                    queryset=Auction.objects.filter(
                        id__in=recent_auction_ids,
                        status="active",
                    ),
                    to_attr="recent_auction",
                )
            )
            paginator = Paginator(artworks, 10)
            page_number = request.GET.get("page")
            page_obj = paginator.get_page(page_number)
            context["page_obj"] = page_obj
        else:
            # No search query was entered
            context["error"] = "Please enter a search term."
        return render(request, "artwork_list.html", context)


def handler404(request, exception):
    """Error Handler 404 - Page Not Found"""
    return render(request, "errors/404.html", status=404)


def handler500(request):
    """Error Handler 500 - Internal Server Error"""
    return render(request, "errors/500.html", status=500)
