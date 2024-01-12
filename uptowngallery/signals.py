import logging
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from allauth.account.signals import user_signed_up
from uptowngallery.models import UserProfile, Artwork

User = get_user_model()
logger = logging.getLogger(__name__)
artwork_approved = Signal()
artwork_denied = Signal()
auction_closed = Signal()
bid_placed = Signal()
profile_updated = Signal()


@receiver(user_signed_up)
def create_user_profile(sender, request, user, **kwargs):
    """
    Signal receiver to create a
    UserProfile instance when a
    new user signs up.
    Logs the creation process
    and handles any exceptions.
    """
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
    """
    Signal receiver to update the UserProfile
    instance when the User instance is updated.
    Saves the profile and logs any exceptions.
    """
    if not created:
        try:
            logger.info("User updated: Saving UserProfile")
            instance.profile.save()
        except Exception as e:
            logger.error(f"Error in update_user_profile: {e}")


@receiver(post_save, sender=Artwork)
def update_or_create_auction(sender, instance, created, **kwargs):
    """
    Signal receiver to handle the
    post-save event for an Artwork instance.
    If the artwork's approval status is 'approved',
    it triggers the auction approval process.
    """
    logger.info(
        f"Artwork post_save signal
        triggered for Artwork ID: {instance.id}, Created: {created}"
    )
    if instance.approval_status == "approved":
        instance.approve_and_start_auction()


@receiver(user_signed_up)
def user_signed_up_(request, user, **kwargs):
    """
    Signal receiver to send a
    welcome email to the user upon successful sign-up.
    """
    send_mail(
        "Welcome to Uptown Gallery",
        "Thank I for signing up for our site!",
        "mailto@uptowngallery.com",
        [user.email],
        fail_silently=False,
    )


@receiver(artwork_approved)
def send_artwork_approval_notification(
    sender, artwork, request, **kwargs
):
    """
    Signal receiver to send
    an email notification when an artwork is approved.
    Notifies the artist that
    their artwork has been approved and the auction has started.
    """
    send_mail(
        "Your Artwork Has Been Approved!",
        'Your artwork "{}" has been approved and your auction has started.'.
        format(
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
    """
    Signal receiver to send an
    email notification when an artwork is denied.
    Notifies the artist that their
    artwork has been denied and will be deleted.
    """
    send_mail(
        "Your Artwork Has Been Denied",
        'Your artwork"{}"has been denied and will be deleted.'
        .format(
            artwork.title
        ),
        "mailto@uptowngallery.com",
        [artwork.artist.user.email],
        fail_silently=False,
    )


@receiver(auction_closed)
def auction_closed_email_notification(sender, auction, **kwargs):
    """
    Signal receiver to send
    an email notification when an auction is closed.
    Notifies the artist
    of the auction's closure.
    """
    artist_user_email = auction.artwork.artist.user.email
    subject = f"Auction for {auction.artwork.title} has ended"
    message = (
        f"Dear {auction.artwork.artist.name},\n\n"
        f"The auction for the artwork '{auction.artwork.title}' has ended."
    )
    from_email = "mailto@uptownfgallery.com"
    recipient_list = [artist_user_email]
    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        fail_silently=False,
    )


@receiver(bid_placed)
def send_notification_emails(sender, bid, user, **kwargs):
    """
    Signal receiver to
    send email notifications upon placing a bid.
    Notifies both the bidder
    and the artwork's artist about the new bid.
    """
    send_mail(
        subject="Bid Confirmation",
        message=f"Your bid of {bid.amount} has been
        placed successfully on {bid.auction.artwork.title}.",
        from_email="mailto@uptownfgallery.com",
        recipient_list=[user.email],
        fail_silently=False,
    )
    artist = bid.auction.artwork.artist
    if artist and hasattr(artist, "email") and artist.email:
        send_mail(
            subject="New Bid Placed on Your Artwork",
            message=f"A new bid of {bid.amount}has been placed
            on your artwork '{bid.auction.artwork.title}'
            by user {user.username}.",
            from_email="mailto@uptownfgallery.com",
            recipient_list=[artist.email],
            fail_silently=False,
        )


@receiver(profile_updated)
def send_profile_update_email(sender, user, field, new_value, **kwargs):
    """
    Signal receiver to send
    email notifications when
    a user's profile is updated.
    Handles specific fields
    like 'shipping_address'.
    """
    if field == "shipping_address":
        send_mail(
            subject="Shipping Address Updated",
            message=f"Your shipping address has been updated to: {new_value}.",
            from_email="mailto@uptownfgallery.com",
            recipient_list=[user.email],
            fail_silently=False,
        )


@receiver(profile_updated)
def send_profile_update_email(sender, user, field, new_value, **kwargs):
    """
    Signal receiver to send
    email notifications when
    a user's profile is updated.
    Handles specific fields like 'name'.
    """
    if field == "name":
        send_mail(
            subject="Name Updated",
            message=f"Your name has been updated to: {new_value}.",
            from_email="mailto@uptownfgallery.com",
            recipient_list=[user.email],
            fail_silently=False,
        )