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
artwork_approved = Signal()
artwork_denied = Signal()
auction_closed = Signal()
bid_placed = Signal()
profile_updated = Signal()


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
        "Your Artwork Has Been Approved!",
        'Your artwork "{}" has been approved and your auction has started.'.format(
            artwork.title
        ),
        "mailto@uptowngallery.com",
        [artwork.artist.user.email],
        fail_silently=False,
    )


@receiver(artwork_denied)
def send_artwork_denial_notification(
    sender, artwork, request, **kwargs
):
    send_mail(
        "Your Artwork Has Been Denied",
        'Unfortunately, your artwork "{}" has been denied and will be deleted.'.format(
            artwork.title
        ),
        "mailto@uptowngallery.com",
        [artwork.artist.user.email],  # Use the user's email
        fail_silently=False,
    )


@receiver(auction_closed)
def auction_closed_email_notification(sender, auction, **kwargs):
    # Accessing the artist's user's email based on my models' structure
    artist_user_email = auction.artwork.artist.user.email

    # Define the email content
    subject = f"Auction for {auction.artwork.title} has ended"
    message = (
        f"Dear {auction.artwork.artist.name},\n\n"
        f"The auction for the artwork '{auction.artwork.title}' has ended."
    )
    from_email = (
        "mailto@uptownfgallery.com"  # replace with my actual email
    )

    # Using the correctly accessed email
    recipient_list = [artist_user_email]

    # Send the email
    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        fail_silently=False,
    )


@receiver(bid_placed)
def send_notification_emails(sender, bid, user, **kwargs):
    # Sending email to the bidder
    send_mail(
        subject="Bid Confirmation",
        message=f"Your bid of {bid.amount} has been placed successfully on {bid.auction.artwork.title}.",
        from_email="mailto@uptownfgallery.com",
        recipient_list=[user.email],
        fail_silently=False,
    )

    # Sending email to the artist if the artist is defined and has an email attribute
    artist = bid.auction.artwork.artist
    if artist and hasattr(artist, "email") and artist.email:
        send_mail(
            subject="New Bid Placed on Your Artwork",
            message=f"A new bid of {bid.amount} has been placed on your artwork '{bid.auction.artwork.title}' by user {user.username}.",
            from_email="mailto@uptownfgallery.com",
            recipient_list=[artist.email],
            fail_silently=False,
        )


@receiver(profile_updated)
def send_profile_update_email(sender, user, field, new_value, **kwargs):
    if field == "shipping_address":
        send_mail(
            subject="Shipping Address Updated",
            message=f"Your shipping address has been updated to: {new_value}.",
            from_email="mailto@uptownfgallery.com",
            recipient_list=[user.email],
            fail_silently=False,
        )
