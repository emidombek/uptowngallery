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
            "approval_status",
        ]


class ArtworkCreateForm(forms.ModelForm):
    class Meta:
        model = Artwork
        exclude = ["approved", "auction_start"]

    def save(self, commit=True):
        # Get the instance of the artwork without saving it to the database
        artwork = super().save(commit=False)

        # Set the artist before saving the artwork
        artwork.artist = self.user_profile
        # UserProfile for each user

        if commit:
            artwork.save()

        return artwork
