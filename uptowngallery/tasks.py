from background_task import background
from django.utils import timezone
from .models import Auction  # Replace with my actual model import


@background(schedule=60)
def update_auction_status():
    now = timezone.now()
    ended_auctions = Auction.objects.filter(
        end_date__lte=now, is_active=True
    )
    for auction in ended_auctions:
        auction.status = "closed"
        auction.is_active = False
        auction.save()
