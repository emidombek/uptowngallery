# forms.py
from django import forms
from .models import Artwork, Auction


class ArtworkCreateForm(forms.ModelForm):
    AUCTION_DURATION_CHOICES = [
        (3, "3 days"),
        (5, "5 days"),
        (7, "7 days"),
    ]

    auction_duration = forms.ChoiceField(
        label="Duration",
        choices=AUCTION_DURATION_CHOICES,
        widget=forms.Select(
            attrs={"class": "form-control custom-form"}
        ),
    )

    class Meta:
        model = Artwork
        exclude = ["approved", "auction_start"]
        widgets = {
            "description": forms.Textarea(
                attrs={
                    "class": "form-control description-section",
                    "placeholder": "Enter artwork description.",
                }
            ),
            "image": forms.FileInput(
                attrs={
                    "class": "form-control image-section",
                    "placeholder": "Upload artwork image.",
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "form-control category-section",
                    "placeholder": "Select artwork category.",
                }
            ),
            "reserve_price": forms.NumberInput(
                attrs={
                    "class": "form-control reserve-price-section",
                    "placeholder": "Enter reserve price.",
                }
            ),
        }

    def save(self, commit=True, user_profile=None):
        artwork = super().save(commit=False)

        if user_profile:
            artwork.artist = user_profile

        if commit:
            artwork.save()

            # Get the selected auction duration
            duration = int(self.cleaned_data.get("auction_duration"))

            # Start an auction for the artwork with the selected duration
            Auction.objects.create(
                artwork=artwork, status="pending", duration=duration
            )

        return artwork
