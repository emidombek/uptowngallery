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

    def __init__(self, *args, **kwargs):
        super(ArtworkForm, self).__init__(*args, **kwargs)
        self.fields["description"].widget.attrs[
            "class"
        ] = "art-description-form-field"
        self.fields["description"].widget.attrs["rows"] = 4
        self.fields["description"].widget.attrs["cols"] = 40
        self.fields["description"].widget.attrs["resize"] = "none"


class ArtworkCreateForm(forms.ModelForm):
    class Meta:
        model = Artwork
        exclude = ["approved", "auction_start"]

    def __init__(self, *args, **kwargs):
        super(ArtworkCreateForm, self).__init__(*args, **kwargs)

        self.fields["description"].widget.attrs[
            "placeholder"
        ] = "Enter artwork description."
        self.fields["image"].widget.attrs[
            "placeholder"
        ] = "Upload artwork image."
        self.fields["category"].widget.attrs[
            "placeholder"
        ] = "Select artwork category."
        self.fields["reserve_price"].widget.attrs[
            "placeholder"
        ] = "Enter reserve price."

    def save(self, commit=True, user_profile=None):
        artwork = super().save(commit=False)

        if user_profile:
            artwork.artist = user_profile

        if commit:
            artwork.save()

        return artwork
