from django import forms
from .models import Artwork, Auction, Bids
import cloudinary.uploader
from decimal import Decimal, InvalidOperation
from allauth.account.forms import SignupForm
from django.contrib.auth import get_user_model
from .models import UserProfile
from django.core.exceptions import ValidationError


class ArtworkCreateForm(forms.ModelForm):
    """
    ArtworkCreateForm:
    Django ModelForm for creating & validating
    artwork forms for auctions.
    Auction Duration Choices:
    Offers 3, 5, or 7 days as auction duration options.
    Fields:
    Includes fields from Artwork model
    except 'approved', 'auction_start'.
    Custom Fields:
    'auction_duration'
    with dropdown choices.
    Validation:
    clean_reserve_price:
    Validates and formats reserve
    price as a positive decimal.
    Initialization (__init__):
    Customizes 'reserve_price'
    field with specific attributes.
    Save Method:
    Creates Artwork instance,
    optionally linking to a user profile.
    ploads image to Cloudinary and saves the URL.
    Creates associated Auction object with status
    'pending' and sets duration.
    Purpose: Manages creation and
    validation of artwork entries for auctions, including
    reserve price formatting, image management,
    and auction duration settings.
    """

    AUCTION_DURATION_CHOICES = [
        (3, "3 days"),
        (5, "5 days"),
        (7, "7 days"),
        (30, "30 days"),
        (60, "60 days"), 
    ]

    auction_duration = forms.ChoiceField(
        label="Duration",
        choices=AUCTION_DURATION_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta:
        model = Artwork
        exclude = ["approved", "auction_start"]
        fields = [
            "title",
            "description",
            "image",
            "category",
            "reserve_price",
            "auction_duration",
        ]

    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get("image")
        print("Clean method executed")

    def __init__(self, *args, **kwargs):
        super(ArtworkCreateForm, self).__init__(*args, **kwargs)
        widget = forms.NumberInput(attrs={
            'step': '0.01',
            'class': 'form-control custom-reserve',
            'title': 'Enter a number with upto two decimal places.'
        })

    def clean_reserve_price(self):
        reserve_price = self.cleaned_data.get("reserve_price")
        if reserve_price:
            try:
                reserve_price = Decimal(reserve_price).quantize(
                    Decimal("0.00")
                )
            except (InvalidOperation, ValueError, TypeError):
                raise forms.ValidationError(
                    "Please enter a valid reserve price in the format XXX.XX."
                )

            if reserve_price < Decimal("0.00"):
                raise forms.ValidationError(
                    "Reserve price must be positive."
                )

            return reserve_price

        else:
            raise forms.ValidationError("This field is required.")

    def save(self, commit=True, user_profile=None):
        artwork = super().save(commit=False)

        if user_profile:
            artwork.artist = user_profile

        if commit:
            try:
                artwork.save()
                image = self.cleaned_data.get("image")
                if image:
                    upload_result = cloudinary.uploader.upload(image)
                    artwork.image_url = upload_result.get("url")
                duration = int(
                    self.cleaned_data.get("auction_duration")
                )
                Auction.objects.create(
                    artwork=artwork, status="pending", duration=duration
                )
            except Exception as e:
                print(f"Error saving artwork: {e}")

        return artwork


class CustomSignupForm(SignupForm):
    """
    This form extends the default
    SignupForm for user registration.
    Additional fields are added to
    capture more user details like name,
    address, city, state, country,
    and zipcode. These details are
    important for maintaining user
    profiles and for shipping purposes.

    The form also overrides
    the save method to save the additional
    information into the UserProfile model,
    ensuring that all user
    data is captured and stored correctly.
    """
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
    zipcode = forms.CharField(max_length=20, label="Zipcode")

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
            "zipcode",
        ]

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        name = self.cleaned_data.get("name")
        street_address = self.cleaned_data.get("street_address")
        city = self.cleaned_data.get("city")
        state = self.cleaned_data.get("state")
        country = self.cleaned_data.get("country")
        zipcode = self.cleaned_data.get("zipcode")
        shipping_address = (
            f"{street_address}, {city}, {state}, {country}, {zipcode}"
        )
        UserProfile.objects.update_or_create(
            user=user,
            defaults={
                "name": name,
                "shipping_address": shipping_address,
            },
        )
        return user


class BidForm(forms.ModelForm):
    """
    This form is used for placing bids in an auction.
    It is tied to the 'Bids' model.

    The form only includes one field,
    'amount', which represents the bid amount.
    During the form's initialization,
    it accepts an 'auction' argument which is
    used for additional validations.

    The 'clean_amount' method is overridden
    to include custom validation logic:
    Ensures that the amount is not None
    and is a positive value.
    Validates that the bid amount is not
    lower than the auction's reserve price.
    Checks against the current highest bid in the auction to ensure that
    the new bid is higher than any existing bids.

    Raises a ValidationError if any of these conditions are not met,
    ensuring the integrity of the bidding process.
    """

    class Meta:
        model = Bids
        fields = ["amount"]

    def __init__(self, *args, **kwargs):
        self.auction = kwargs.pop("auction", None)
        super().__init__(*args, **kwargs)

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount is None:
            raise forms.ValidationError("This field is required.")
        if amount < 0:
            raise forms.ValidationError("Bid amount must be positive.")
        if self.auction:
            if amount < self.auction.reserve_price:
                raise ValidationError(
                    "Bid amount cannot be lower than the reserve price."
                )
            current_highest_bid = self.auction.bids.order_by(
                "-amount"
            ).first()
            if (
                current_highest_bid
                and amount <= current_highest_bid.amount
            ):
                raise ValidationError(
                    "Your bid is not higher than the current highest bid."
                )
        return amount


class ArtworkEditForm(forms.ModelForm):
    class Meta:
        model = Artwork
        fields = ["title", "description"]
