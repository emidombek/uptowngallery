import datetime
from django.contrib import admin
from django.db import transaction
from .models import Artwork, Auction
from .forms import ArtworkCreateForm


class ArtworkAdmin(admin.ModelAdmin):
    list_display = (
        "artist",
        "approved",
        "auction_start",
        "create_date",
        "description",
        "image",
    )
    list_filter = ("approved",)
    actions = ["approve_artworks"]

    def get_form(self, request, obj=None, **kwargs):
        if request.user.groups.filter(name="Artist").exists():
            return ArtworkCreateForm
        return super().get_form(request, obj, **kwargs)

    def approve_artworks(self, request, queryset):
        queryset.update(
            approved=True, auction_start=datetime.datetime.now()
        )

    approve_artworks.short_description = "Approve selected artworks"

    exclude = ["approved", "auction_start"]

    def delete_queryset(self, request, queryset):
        """
        This method is called when admin tries to delete artworks in bulk from the admin interface.
        """
        with transaction.atomic():  # Use a transaction to ensure deletion
            for artwork in queryset:
                # Handle or delete related auctions first
                Auction.objects.filter(artwork=artwork).delete()
                artwork.delete()  # Then delete the artwork itself

    def delete_model(self, request, obj):
        """
        This method is called when an admin tries to delete a single artwork instance.
        """
        with transaction.atomic():  # Use a transaction to ensure atomic deletion
            # Handle or delete related auctions first
            Auction.objects.filter(artwork=obj).delete()
            obj.delete()  # Then delete the artwork itself


admin.site.register(Artwork, ArtworkAdmin)
