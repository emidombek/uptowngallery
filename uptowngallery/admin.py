from django.db import transaction
from django.utils import timezone
from django.contrib import admin
from .forms import ArtworkCreateForm
from .models import Artwork, Auction
from .signals import artwork_approved, artwork_denied


class ArtworkAdmin(admin.ModelAdmin):
    """
    Custom admin interface for the Artwork model.
    Defines how artworks are displayed,
    filtered, and modified in the Django admin interface.
    """

    list_display = (
        "artist",
        "approved",
        "auction_start",
        "create_date",
        "description",
        "image",
    )
    list_filter = ("approved",)
    actions = ["approve_artworks", "deny_artworks"]

    def get_form(self, request, obj=None, **kwargs):
        if request.user.groups.filter(name="Artist").exists():
            return ArtworkCreateForm
        return super(ArtworkAdmin, self).get_form(
            request, obj, **kwargs
        )

    def approve_artworks(self, request, queryset):
        queryset.update(approved=True, auction_start=timezone.now())
        for artwork in queryset:
            artwork_approved.send(
                sender=self.__class__, artwork=artwork, request=request
            )

    approve_artworks.short_description = "Approve selected artworks"
    exclude = ["approved", "auction_start"]

    def deny_artworks(self, request, queryset):
        queryset.update(approved=False)
        for artwork in queryset:
            artwork_denied.send(
                sender=self.__class__, artwork=artwork, request=request
            )

    deny_artworks.short_description = "Deny selected artworks"

    def delete_queryset(self, request, queryset):
        """
        This method is called when admin
        tries to delete artworks in bulk
        from the admin interface.
        """
        with transaction.atomic():
            for artwork in queryset:
                Auction.objects.filter(artwork=artwork).delete()
                artwork.delete()

    def delete_model(self, request, obj):
        """
        This method is called when an admin
        tries to delete a single artwork instance.
        """
        with transaction.atomic():
            Auction.objects.filter(artwork=obj).delete()
            obj.delete()


admin.site.register(Artwork, ArtworkAdmin)

class AuctionAdmin(admin.ModelAdmin):
    list_display = ("id", "artwork", "status", "end_date")  
    list_editable = ("status",)  

admin.site.register(Auction, AuctionAdmin)
