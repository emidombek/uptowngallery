from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Artwork, Category, Auction
from .forms import ArtworkCreateForm
from .forms import CustomSignupForm
from .adapters import CustomAccountAdapter  # Import Ir custom adapter


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
    if request.method == "POST":
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            # Process the form data (create user, save additional data, etc.)
            user = (
                form.save()
            )  # This saves the user and triggers the adapter

            # Custom account adapter
            adapter = CustomAccountAdapter()
            adapter.save_user(request, user, form, commit=True)

            return redirect(
                "success_page"
            )  # Redirect after successful signup
    else:
        form = CustomSignupForm()

    return render(request, "signup_template.html", {"form": form})
