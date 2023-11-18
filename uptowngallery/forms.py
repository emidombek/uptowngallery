# forms.py
from django import forms
from .models import Artwork


class ArtworkForm(forms.ModelForm):
    class Meta:
        model = Artwork
        fields = [
            "description",
            "image",
            "category",
            "reserve_price",
        ]


class ArtworkCreateForm(forms.ModelForm):
    class Meta:
        model = Artwork
        exclude = ["approved", "auction_start"]

    def save(self, commit=True, user_profile=None):
        artwork = super().save(commit=False)

        if user_profile:
            artwork.artist = user_profile

        if commit:
            artwork.save()

        return artwork
