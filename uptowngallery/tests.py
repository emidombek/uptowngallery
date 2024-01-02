from datetime import timedelta
from unittest.mock import patch
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from .models import (
    Artwork,
    UserProfile,
    Auction,
    Bids,
)


class UserProfileModelTest(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(
            username="testuser", password="12345"
        )
        # Create a user profile for the user
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            name="Test User",
            shipping_address="123 Test St",
        )

    def test_user_profile_creation(self):
        self.assertIsInstance(self.user_profile, UserProfile)
        self.assertEqual(self.user_profile.user, self.user)
        self.assertEqual(self.user_profile.name, "Test User")

    def test_string_representation(self):
        expected_string = f"User Profile for {self.user.username} - Name: {self.user_profile.name} - Shipping Address: {self.user_profile.shipping_address} - Created on: {self.user_profile.create_date}"
        self.assertEqual(str(self.user_profile), expected_string)

    def test_create_date_default(self):
        # Assuming the profile was created just moments ago
        self.assertAlmostEqual(
            self.user_profile.create_date,
            timezone.now(),
            delta=timedelta(seconds=30),
        )

    def test_one_to_one_relationship_with_user(self):
        # Attempting to create another UserProfile for the same user should raise an IntegrityError
        with self.assertRaises(
            Exception
        ):  # Replace with specific exception if known
            UserProfile.objects.create(
                user=self.user, name="Another Test User"
            )


class ArtworkModelTests(TestCase):
    def setUp(self):
        # Create a test user and user profile
        self.user = User.objects.create_user(
            username="testuser", password="12345"
        )
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            name="Test User",
            shipping_address="123 Test Street",
        )

        # Create a test artwork
        self.artwork = Artwork.objects.create(
            artist=self.user_profile,
            title="Test Artwork",
            description="A test description",
            category="painting",
            reserve_price=100.00,
        )

    def test_artwork_creation(self):
        # Verify artwork was created correctly with its attributes
        self.assertEqual(self.artwork.title, "Test Artwork")
        self.assertEqual(self.artwork.artist, self.user_profile)
        self.assertEqual(self.artwork.description, "A test description")
        self.assertEqual(self.artwork.category, "painting")
        self.assertEqual(self.artwork.reserve_price, 100.00)

    def test_string_representation(self):
        # Test the custom string representation of artwork
        expected_string = f"Artwork #{self.artwork.id} - Title: {self.artwork.title} - Artist: {self.artwork.artist}"
        self.assertEqual(str(self.artwork), expected_string)

    def test_calculate_price(self):
        # Test scenario with no bids - should return reserve price
        self.assertEqual(self.artwork.calculate_price(), 100.00)

        # Set up and test scenario with bids
        auction = Auction.objects.create(
            artwork=self.artwork, status="active", reserve_price=100.00
        )
        bid1 = Bids.objects.create(auction=auction, amount=150)
        bid2 = Bids.objects.create(
            auction=auction, amount=200
        )  # highest bid

        self.assertEqual(self.artwork.calculate_price(), 200)

    def test_approve_and_start_auction_creates_auction_after_admin_approval(
        self,
    ):
        # Simulate admin action by setting the approval status to approved
        self.artwork.approval_status = "approved"
        self.artwork.save()

        # Now call the method under test
        self.artwork.approve_and_start_auction()

        # Refresh from db to get updated values
        self.artwork.refresh_from_db()
        auction = Auction.objects.filter(artwork=self.artwork).first()

        # Check the approval status and auction details
        self.assertEqual(self.artwork.approval_status, "approved")
        self.assertIsNotNone(auction)
        self.assertTrue(auction.is_active)
        self.assertEqual(auction.status, "active")


class AuctionModelTests(TestCase):
    def setUp(self):
        # Create regular user and admin user
        self.user = User.objects.create_user(
            username="testuser", password="testpass"
        )
        self.admin_user = User.objects.create_superuser(
            username="adminuser", password="adminpass"
        )

        # Create UserProfile linked to my user
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            name="Test Artist",
            shipping_address="123 Street",
        )

        # Create an artwork that is initially not approved
        self.artwork = Artwork.objects.create(
            artist=self.user_profile,
            title="Test Artwork",
            description="A beautiful artwork",
            category="painting",
            reserve_price=100.00,
        )

    def test_artwork_approval_triggers_auction_creation(self):
        # Login as admin to perform approval actions
        self.client.login(username="adminuser", password="adminpass")

        # Simulate approving the artwork
        self.artwork.approval_status = "approved"
        self.artwork.save()  # Assuming this triggers auction creation

        # Verify that an auction has been created for the artwork
        self.assertTrue(self.artwork.auctions.exists())

        # Check that the auction is in the active status
        auction = self.artwork.auctions.first()
        self.assertIsNotNone(auction)
        self.assertEqual(auction.status, "active")

    def test_auction_closure(self):
        # Simulate artwork approval and auction creation
        self.artwork.approval_status = "approved"
        self.artwork.save()
        auction = self.artwork.auctions.first()

        # Mock the current time to simulate auction closure
        with patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = auction.end_date + timedelta(
                minutes=1
            )

            # Simulate auction closure
            auction.status = "closed"
            auction.save()

        # Verify that the auction is now closed
        updated_auction = Auction.objects.get(id=auction.id)
        self.assertEqual(updated_auction.status, "closed")

    def tearDown(self):
        # Logout and cleanup any necessary data
        self.client.logout()


class BidModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            "testuser", "test@example.com", "password"
        )
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            name="John Doe",
            shipping_address="123 Test St",
        )

        self.artwork = Artwork.objects.create(
            artist=self.user_profile,
            title="Sample Artwork",
            description="Sample Artwork Description",
            category="painting",
            reserve_price=100.00,
            # Ensure I set other required fields
        )

        self.auction = Auction.objects.create(
            artwork=self.artwork,
            status="active",
            reserve_price=100,
            # Ensure I set other required fields
        )

    def test_create_valid_bid(self):
        # Create a bid with all necessary valid fields
        bid = Bids.objects.create(
            bidder=self.user_profile,
            auction=self.auction,
            amount=150,  # A positive amount
        )

        # Ensure bid is created successfully
        self.assertEqual(Bids.objects.count(), 1)
        self.assertEqual(bid.amount, 150)
        self.assertEqual(bid.bidder, self.user_profile)
        self.assertEqual(bid.auction, self.auction)

    def test_negative_bid_amount(self):
        # Attempt to create a bid with a negative amount
        with self.assertRaises(ValidationError):
            Bids.objects.create(
                bidder=self.user_profile,
                auction=self.auction,
                amount=-50,  # A negative amount
            ).clean()  # This will call the clean method to validate

    def test_bid_time_auto_set(self):
        # Create a bid and ensure the bid_time is automatically set
        bid = Bids.objects.create(
            bidder=self.user_profile,
            auction=self.auction,
            amount=200,
        )

        # bid_time should be close to now
        self.assertAlmostEqual(
            bid.bid_time,
            timezone.now(),
            delta=timezone.timedelta(seconds=30),
        )


class LandingPageViewTests(TestCase):
    def test_landing_page_loads_correctly(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        # Check that recent artworks are in the context and correct
        self.assertTrue("recent_artworks" in response.context)


class ArtworkListViewTests(TestCase):
    def test_artwork_list_loads_correctly(self):
        response = self.client.get(reverse("artwork_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "artwork_list.html")
        self.assertTrue("page_obj" in response.context)


class CreateArtworkViewTests(TestCase):
    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass",
        )

        # Additional setup like creating related objects if needed

    def test_create_artwork_post_success(self):
        # Log the user in
        self.client.login(username="testuser", password="testpass")

        # Prepare post data for my artwork creation form
        post_data = {
            "title": "New Artwork",
            "description": "Beautiful Artwork",
            "category": "painting",
            # ... include other form fields as necessary
        }

        # Send a POST request to the view meant to create an artwork
        response = self.client.post(
            reverse("create-artwork"), post_data
        )  # Adjust with my actual url name

        # Check the response and object creation status
        self.assertEqual(
            response.status_code, 302
        )  # Redirect means success in this case
        self.assertTrue(
            Artwork.objects.filter(title="New Artwork").exists()
        )  # Confirm the object was created


class CreateArtworkViewTests(TestCase):
    def setUp(self):
        # Create a test user and profile
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            name="Test User",
            shipping_address="123 Test St",
        )
        self.client.login(username="testuser", password="testpassword")

    def test_create_artwork_post_success(self):
        # Make sure to include all required fields for my form
        post_data = {
            "title": "New Artwork",
            "description": "Beautiful Artwork",
            "image": "image/upload/path.jpg",  # Assuming it's a file path or use SimpleUploadedFile for actual file
            "category": "painting",
            "reserve_price": 100.00,
            "auction_duration": "3",  # Adjust with my valid choices or actual field format
        }
        response = self.client.post(
            reverse("create_artwork"), post_data
        )
        self.assertEqual(
            response.status_code, 302
        )  # Redirects on success
        self.assertTrue(
            Artwork.objects.filter(title="New Artwork").exists()
        )

    def test_create_artwork_without_login(self):
        self.client.logout()  # Ensure no user is logged in
        post_data = {
            "title": "New Artwork",
            "description": "Beautiful Artwork",
            "image": "image/upload/path.jpg",  # Assuming it's a file path or use SimpleUploadedFile for actual file
            "category": "painting",
            "reserve_price": 100.00,
            "auction_duration": "3",  # Adjust with my valid choices or actual field format
        }
        response = self.client.post(
            reverse("create_artwork"), post_data
        )
        self.assertNotEqual(
            response.status_code, 200
        )  # Should not be able to post without login
        self.assertFalse(
            Artwork.objects.filter(title="New Artwork").exists()
        )


class PendingArtworksViewTests(TestCase):
    def setUp(self):
        # Create a user and profile
        self.user = User.objects.create_user(
            username="testuser", password="12345"
        )
        self.profile = UserProfile.objects.create(
            user=self.user
        )  # Create the profile related to the user
        self.client.login(username="testuser", password="12345")

        # Create 15 artworks, all pending approval
        for i in range(15):
            Artwork.objects.create(
                artist=self.profile,
                title=f"Artwork {i}",
                approved=False,  # All artworks are pending (unapproved)
            )

    def test_pending_artworks_display(self):
        response = self.client.get(reverse("pending_artworks"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pending_artworks.html")

        # Ensure only unapproved artworks for the user are listed
        artworks_in_context = response.context["artworks"]
        self.assertTrue(
            all(
                artwork.approved == False
                for artwork in artworks_in_context
            )
        )

        # Check the number of artworks returned
        # Assuming that there are more than 10 artworks, it should return only 10 due to pagination
        self.assertTrue(len(artworks_in_context) <= 10)

    def test_pagination(self):
        # Test the first page
        response = self.client.get(
            reverse("pending_artworks") + "?page=1"
        )
        self.assertEqual(len(response.context["artworks"]), 10)

        # Test the second page
        response = self.client.get(
            reverse("pending_artworks") + "?page=2"
        )
        self.assertTrue(
            len(response.context["artworks"]) > 0
        )  # Assuming there's a second page

    def test_access_control(self):
        # Ensure user is logged out
        self.client.logout()

        # Attempt to access the page
        response = self.client.get(reverse("pending_artworks"))

        # Check if redirected to login page
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            response.url.startswith(reverse("account_login"))
        )
