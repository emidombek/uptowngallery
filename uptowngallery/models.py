from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from cloudinary.models import CloudinaryField
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


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
    name = models.CharField(
        max_length=255,
        null=True,
        verbose_name="Name",
        help_text="The name of the user.",
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
        return f"User Profile for {self.user.username} - Name: {self.name} - Shipping Address: {self.shipping_address} - Created on: {self.create_date}"


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

    title = models.CharField(
        max_length=255,
        null=True,
        verbose_name="Title",
        help_text="The title of the artwork.",
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

    APPROVAL_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]
    approval_status = models.CharField(
        max_length=20, choices=APPROVAL_CHOICES, default="pending"
    )

    auction_start = models.DateTimeField(null=True, blank=True)

    AUCTION_DURATION_CHOICES = (
        ("3", "3 days"),
        ("5", "5 days"),
        ("7", "7 days"),
    )

    auction_duration = models.CharField(
        max_length=8,
        choices=AUCTION_DURATION_CHOICES,
        default="3_days",  # Set Ir default duration if needed
    )

    reserve_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        verbose_name="Reserve Price",
        help_text="The minimum price at which the artwork can be sold.",
    )

    class Meta:
        ordering = ["-create_date"]

    def calculate_price(self):
        related_auctions = self.auction_set.all()
        if related_auctions:
            bids = Bids.objects.filter(auction__in=related_auctions)
            if bids:
                highest_bid = max(bids, key=lambda bid: bid.amount)
                return highest_bid.amount
            return self.reserve_price
        return self.reserve_price

    def __str__(self):
        return f"Artwork #{self.id} - Title: {self.title} - Artist: {self.artist}"

    def approve_and_start_auction(self):
        if not self.approved:
            return  # Auction cannot be started for unapproved artworks

        auction_start = timezone.now()
        auction_end = self.calculate_auction_end_date(auction_start)

        auction, created = Auction.objects.get_or_create(
            artwork=self,
            defaults={
                "create_date": auction_start,
                "end_date": auction_end,
                "reserve_price": self.reserve_price,
                "status": "active",  # Change status to active
                "is_active": 1,  # Set is_active to 1
            },
        )

        if not created:
            auction.create_date = auction_start
            auction.end_date = auction_end
            auction.reserve_price = self.reserve_price
            auction.status = "active"  # Change status to active
            auction.is_active = 1  # Set is_active to 1
            auction.save()

    def calculate_auction_end_date(self, auction_start):
        if self.auction_duration == "3_days":
            duration = timedelta(days=3)
        elif self.auction_duration == "5_days":
            duration = timedelta(days=5)
        elif self.auction_duration == "7_days":
            duration = timedelta(days=7)
        else:
            duration = timedelta(days=3)

        return auction_start + duration


class Auction(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("closed", "Closed"),
        ("cancelled", "Cancelled"),
        ("pending", "Pending"),
    ]
    id = models.AutoField(primary_key=True)

    artwork = models.ForeignKey(
        "Artwork",
        on_delete=models.CASCADE,
        related_name="auctions",
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
        default="pending",
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

    def close_auction(self):
        if self.status == "active" and self.end_date <= timezone.now():
            self.status = "closed"  # Change status to closed
            self.is_active = 0  # Set is_active to 0
            self.save()


@receiver(post_save, sender=Artwork)
def artwork_approval_handler(sender, instance, created, **kwargs):
    if created:
        # Automatically approve and start the auction when an artwork is created
        instance.approve_and_start_auction()
    else:
        # If the artwork is updated (e.g., approval status changes), handle it here
        if instance.approval_status == "approved":
            instance.approve_and_start_auction()
        elif instance.approval_status == "rejected":
            # Handle rejection logic here (e.g., cancel the auction)
            instance.auction.status = "cancelled"
            instance.auction.is_active = 0
            instance.auction.save()


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
        default=timezone.now,
        verbose_name="Bid Time",
        help_text="The date and time when the bid was placed.",
    )

    def clean(self):
        if self.amount < 0:
            raise ValidationError(
                "Bid amount must be a positive integer."
            )
