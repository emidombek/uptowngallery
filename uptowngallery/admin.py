from django.contrib import admin
from .models import Artwork


class ArtworkAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "artist",
        "approved",
        "create_date",
        "description",
        "image",
    )
    list_filter = ("approved",)
    actions = ["approve_artworks"]

    def approve_artworks(self, request, queryset):
        queryset.update(approved=True)

    approve_artworks.short_description = "Approve selected artworks"


admin.site.register(Artwork, ArtworkAdmin)
