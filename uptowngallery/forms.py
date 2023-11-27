# forms.py
from django import forms
from .models import Artwork, Auction
import cloudinary.uploader
from allauth.account.forms import SignupForm
from django.contrib.auth import get_user_model
from .models import UserProfile


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
    street_address = forms.CharField(
        max_length=255, label="Street Address"
    )
    city = forms.CharField(max_length=255, label="City")
    state = forms.CharField(max_length=255, label="State")
    country = forms.ChoiceField(
        choices=[("US", "United States"), ("CA", "Canada")],
        label="Country",
    )

    class Meta:
        model = get_user_model()
        fields = [
            "email",
            "password1",
            "password2",
            "name",
            "street_address",
            "city",
            "state",
            "country",
        ]

    def save(self, request):
        # Get the user instance from the parent class's save method
        user = super(CustomSignupForm, self).save(request)

        # Get the address fields from the form
        street_address = self.cleaned_data.get("street_address")
        city = self.cleaned_data.get("city")
        state = self.cleaned_data.get("state")
        country = self.cleaned_data.get("country")

        # Concatenate the address fields into a single string
        shipping_address = (
            f"{street_address}, {city}, {state}, {country}"
        )

        # Create or update the user's profile with the shipping address
        UserProfile.objects.update_or_create(
            user=user, defaults={"shipping_address": shipping_address}
        )

        return user
