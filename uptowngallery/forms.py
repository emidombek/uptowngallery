# forms.py
from django import forms
from .models import Artwork


class ArtworkForm(forms.ModelForm):
    class Meta:
        model = Artwork
        fields = [
            "artist",
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
