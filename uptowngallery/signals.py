# signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from django.contrib.auth import get_user_model
from uptowngallery.models import UserProfile, Artwork, Auction
from django.utils import timezone


User = get_user_model()


# Signal handler to create or update UserProfile
@receiver(user_signed_up)
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    try:
        if created:
            print("User created")
            UserProfile.objects.create(user=instance)
        else:
            print("User updated")
            instance.profile.save()
    except Exception as e:
        print(f"Error in create_or_update_user_profile: {e}")


@receiver(post_save, sender=Artwork)
def update_or_create_auction(sender, instance, created, **kwargs):
    if instance.approval_status == "approved":
        if created:
            # Create a new auction
            auction = Auction.objects.create(
                artwork=instance,
                create_date=instance.create_date,  # Set to Ir preferred field
                end_date=instance.calculate_auction_end_date(
                    instance.create_date
                ),  # Adjust this logic
                reserve_price=instance.reserve_price,  # Adjust this logic
                status="active",
                is_active=1,
            )
            instance.auction = auction
        else:
            # Update an existing auction if it exists
            if hasattr(instance, "auction"):
                auction = instance.auction
                auction.end_date = instance.calculate_auction_end_date(
                    instance.create_date
                )  # Adjust this logic
                auction.reserve_price = (
                    instance.reserve_price
                )  # Adjust this logic
                auction.status = "active"
                auction.is_active = 1
                auction.save()
