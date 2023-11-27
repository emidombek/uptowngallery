# forms.py
from django import forms
from .models import Artwork, Auction
import cloudinary.uploader
from allauth.account.forms import SignupForm
from django.contrib.auth import get_user_model


class ArtworkCreateForm(forms.ModelForm):
    AUCTION_DURATION_CHOICES = [
        (3, "3 days"),
        (5, "5 days"),
        (7, "7 days"),
    ]

    auction_duration = forms.ChoiceField(
        label="Duration",
        choices=AUCTION_DURATION_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta:
        model = Artwork
        exclude = ["approved", "auction_start"]

    def save(self, commit=True, user_profile=None):
        artwork = super().save(commit=False)

        if user_profile:
            artwork.artist = user_profile

        if commit:
            artwork.save()

            # Upload image to Cloudinary
            image = self.cleaned_data.get("image")
            if image:
                upload_result = cloudinary.uploader.upload(image)
                artwork.image_url = upload_result.get("url")

            # Get the selected auction duration
            duration = int(self.cleaned_data.get("auction_duration"))

            # Start an auction for the artwork with the selected duration
            Auction.objects.create(
                artwork=artwork, status="pending", duration=duration
            )

        return artwork


class CustomSignupForm(SignupForm):
    name = forms.CharField(max_length=255, required=True, label="Name")

    class Meta:
        model = get_user_model()
        fields = [
            "email",
            "password1",
            "password2",
            "name",
            "shipping_address",
        ]
