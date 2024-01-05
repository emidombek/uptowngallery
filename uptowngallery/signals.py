# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from django.contrib.auth import get_user_model
from uptowngallery.models import UserProfile, Artwork
from allauth.account.signals import user_signed_up
from django.dispatch import receiver, Signal
from django.core.mail import send_mail
import logging

User = get_user_model()
logger = logging.getLogger(__name__)
artwork_approved = Signal(providing_args=["artwork", "request"])
artwork_denied = Signal(providing_args=["artwork", "request"])


@receiver(user_signed_up)
def create_user_profile(sender, request, user, **kwargs):
    try:
        logger.info("User created: Creating UserProfile")
        profile, created = UserProfile.objects.get_or_create(user=user)

        if created:
            logger.info(f"Created new profile for {user}")
        else:
            logger.info(f"Found existing profile for {user}")
    except Exception as e:
        logger.error(f"Error in create_user_profile: {e}")


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if not created:
        try:
            logger.info("User updated: Saving UserProfile")
            instance.profile.save()
        except Exception as e:
            logger.error(f"Error in update_user_profile: {e}")


@receiver(post_save, sender=Artwork)
def update_or_create_auction(sender, instance, created, **kwargs):
    logger.info(
        f"Artwork post_save signal triggered for Artwork ID: {instance.id}, Created: {created}"
    )
    if instance.approval_status == "approved":
        instance.approve_and_start_auction()


@receiver(user_signed_up)
def user_signed_up_(request, user, **kwargs):
    # Send an email to the new user
    send_mail(
        "Welcome to Uptown Gallery",
        "Thank I for signing up for our site!",
        "mailto@uptowngallery.com",  # Replace with my sender email
        [user.email],  # User's email address
        fail_silently=False,
    )


@receiver(artwork_approved)
def send_artwork_approval_notification(
    sender, artwork, request, **kwargs
):
    # Send an email notification
    send_mail(
        "My Artwork Has Been Approved!",
        'My artwork "{}" has been approved.'.format(artwork.title),
        "mailto@uptowngallery.com",
        l[artwork.artist.email],  # Replace with the artist's email
        fail_silently=False,
    )


@receiver(artwork_denied)
def send_artwork_denial_notification(
    sender, artwork, request, **kwargs
):
    send_mail(
        "My Artwork Has Been Denied",
        'Unfortunately, my artwork "{}" has been denied and will be deleted.'.format(
            artwork.title
        ),
        "mailto@uptowngallery.com",
        [artwork.artist.email],  # The artist's email
        fail_silently=False,
    )
