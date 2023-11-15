from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField
from django.core.exceptions import ValidationError


class Category(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        blank=True,
        related_name="profile",
        verbose_name="User",
        help_text="Format: Required, Unique",
    )
    shipping_address = models.CharField(
        max_length=255,
        null=True,
        verbose_name="Shipping Address",
        help_text="The shipping address of the user.",
    )
    create_date = models.DateTimeField(
        null=True,
        verbose_name="Create Date",
        help_text="The date when the user profile was created.",
    )

    def __str__(self):
        return f"User Profile for {self.user.username} - Shipping Address: {self.shipping_address} - Created on: {self.create_date}"


class Artwork(models.Model):
    id = models.AutoField(primary_key=True)
    artist = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        null=True,
        verbose_name="Artist",
    )
    create_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Create Date",
        help_text="The date when the artwork was created.",
    )
    description = models.TextField(
        null=True, verbose_name="Description"
    )
    image = CloudinaryField(null=True, blank=True, verbose_name="Image")

    CATEGORY_CHOICES = [
        ("painting", "Painting"),
        ("sculpture", "Sculpture"),
        ("photography", "Photography"),
        ("posters", "Posters"),
        ("portraits", "Portraits"),
        ("contemporary", "Contemporary"),
        ("abstract", "Abstract"),
        ("popart", "Popart"),
        ("classical", "Classical"),
    ]
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, blank=True
    )

    approved = models.BooleanField(
        default=False, verbose_name="Approved"
    )

    auction_start = models.DateTimeField(null=True, blank=True)

    reserve_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        verbose_name="Reserve Price",
        help_text="The minimum price at which the artwork can be sold.",
    )

    def calculate_price(self):
        auctions = self.related_artworks.all()
        if auctions:
            bids = Bids.objects.filter(auction__in=auctions)
            if bids:
                highest_bid = max(bids, key=lambda bid: bid.amount)
                return highest_bid.amount
        return self.reserve_price

    def __str__(self):
        return f"Artwork #{self.id} - Artist: {self.artist}"


class Auction(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("closed", "Closed"),
        ("cancelled", "Cancelled"),
        ("pending", "Pending"),
    ]
    id = models.AutoField(primary_key=True)
    artwork = models.ForeignKey(
        Artwork,
        on_delete=models.CASCADE,
        null=True,
        verbose_name="Artwork",
    )
    create_date = models.DateTimeField(
        null=True,
        verbose_name="Create Date",
        help_text="The date when the auction was created.",
    )
    status = models.CharField(
        max_length=255,
        choices=STATUS_CHOICES,
        default="active",
        null=True,
        verbose_name="Status",
        help_text="The current status of the auction.",
    )
    is_active = models.BooleanField(null=True, verbose_name="Is Active")
    end_date = models.DateTimeField(
        null=True,
        verbose_name="End Date",
        help_text="The date when the auction ends.",
    )
    reserve_price = models.IntegerField(
        null=True,
        verbose_name="Reserve Price",
        help_text="The minimum price at which the artwork can be sold.",
    )

    def __str__(self):
        return f"Auction #{self.id} - {self.status} - Artwork: {self.artwork}"


class Bids(models.Model):
    id = models.AutoField(primary_key=True)
    bidder = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        null=True,
        verbose_name="Bidder",
    )
    auction = models.ForeignKey(
        Auction,
        on_delete=models.CASCADE,
        null=True,
        verbose_name="Auction",
    )
    amount = models.IntegerField(
        null=True,
        verbose_name="Amount",
        help_text="The amount of the bid.",
    )
    bid_time = models.DateTimeField(
        null=True,
        verbose_name="Bid Time",
        help_text="The date and time when the bid was placed.",
    )

    def clean(self):
        if self.amount < self.auction.reserve_price:
            raise ValidationError(
                "Bid amount cannot be lower than the reserve price."
            )
