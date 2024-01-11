from django.utils import timezone
from .models import Auction
from .signals import auction_closed


def check_and_close_auctions():
    """
    Djano Q task that checks if the auction time has elasped and then changes the status of the auction to closed.
    """
    now = timezone.now()
    active_auctions = Auction.objects.filter(
        end_date__lte=now, is_active=True
    )
    for auction in active_auctions:
        auction.status = "closed"
        auction.is_active = False
        auction.save()

    for auction in active_auctions:
        auction.status = "closed"
        auction.save()
        auction_closed.send(sender=None, auction=auction)
