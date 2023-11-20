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
        label="Auction Duration",
        choices=AUCTION_DURATION_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta:
        model = Artwork
        exclude = ["approved", "auction_start"]

    def __init__(self, *args, **kwargs):
        super(ArtworkCreateForm, self).__init__(*args, **kwargs)

        self.fields["auction_duration"] = self.fields.pop(
            "auction_duration"
        )
        self.fields["description"].widget.attrs.update(
            {
                "placeholder": "Enter artwork description.",
                "class": "form-control no-resize",  # Add the 'no-resize' class
            }
        )
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

            # Get the selected auction duration
            duration = int(self.cleaned_data.get("auction_duration"))

            # Start an auction for the artwork with the selected duration
            Auction.objects.create(
                artwork=artwork, status="pending", duration=duration
            )

        return artwork
