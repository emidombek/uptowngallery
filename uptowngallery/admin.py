import datetime
from django.contrib import admin
from .models import Artwork
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


admin.site.register(Artwork, ArtworkAdmin)
