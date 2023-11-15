# forms.py
from django import forms
from .models import Artwork


class ArtworkCreateForm(forms.ModelForm):
    class Meta:
        model = Artwork
        exclude = ["approved", "auction_start"]
