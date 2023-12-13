# signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from django.contrib.auth import get_user_model
from uptowngallery.models import UserProfile, Artwork, Auction
from django.utils import timezone
import logging

User = get_user_model()

logger = logging.getLogger(__name__)


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
    logger.info(
        f"Artwork post_save signal triggered for Artwork: {instance.id}, Created: {created}"
    )

    # Call approve_and_start_auction only when the artwork is approved
    if instance.approval_status == "approved":
        instance.approve_and_start_auction()
