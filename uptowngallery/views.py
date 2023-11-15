from django.shortcuts import render
from django.views import View
from .models import Artwork, Category


class LandingPageView(View):
    def get(self, request):
        top_categories = Category.objects.all()[:9]
        recent_artworks = Artwork.objects.filter(
            approved=True
        ).order_by("-create_date")[:10]
        return render(
            request,
            "landing_page.html",
            {
                "top_categories": top_categories,
                "recent_artworks": recent_artworks,
            },
        )
