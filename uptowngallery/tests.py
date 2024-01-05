from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.contrib.messages import get_messages
from .forms import CustomSignupForm, ArtworkCreateForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.test import TestCase
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
            "image": "image/upload/path.jpg",
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


class CustomSignupViewTests(TestCase):
    def test_get_signup_page(self):
        response = self.client.get(
            reverse("account_signup")
        )  # Changed to 'account_signup'
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/signup.html")
        self.assertIsInstance(
            response.context["form"], CustomSignupForm
        )

    def test_successful_signup(self):
        form_data = {
            "email": "user@example.com",
            "password1": "testpassword",
            "password2": "testpassword",
            "name": "Test User",
            "street_address": "123 Test St",
            "city": "Testville",
            "state": "Testland",
            "country": "US",
            "zipcode": "12345",
        }
        response = self.client.post(
            reverse("account_signup"), form_data
        )
        self.assertEqual(response.status_code, 302)

        # Verify user creation
        user = get_user_model().objects.last()
        self.assertEqual(user.email, "user@example.com")

        # Verify user profile creation
        profile = UserProfile.objects.get(user=user)
        self.assertEqual(
            profile.shipping_address,
            "123 Test St, Testville, Testland, US, 12345",
        )

    def test_form_validation(self):
        # Submit a form with missing or invalid data
        response = self.client.post(
            reverse("signup"), {"email": "invalidemail"}
        )
        self.assertFalse(response.context["form"].is_valid())
        self.assertTemplateUsed(response, "signup_template.html")


class SignupViewTests(TestCase):
    def test_get_signup_page(self):
        # Test that the signup page loads correctly
        response = self.client.get(reverse("account_signup"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "account/signup.html"
        )  # Update template name as per my configuration


class CustomSignupViewTests(TestCase):
    def test_get_signup_page(self):
        # Test that the signup page loads correctly
        response = self.client.get(reverse("account_signup"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "account/signup.html"
        )  # or my custom template if it's different

    def test_successful_signup(self):
        # Test the successful creation of a new user via signup
        form_data = {
            "email": "test@example.com",
            "password1": "complex_password",
            "password2": "complex_password",
            # Add the rest of my form fields here
            "name": "Test User",
            "street_address": "1234 Test St",
            "city": "Testville",
            "state": "Teststate",
            "country": "US",
            "zipcode": "12345",
        }
        response = self.client.post(
            reverse("account_signup"), form_data
        )
        self.assertEqual(
            response.status_code, 302
        )  # Redirect after successful signup

    def test_form_validation(self):
        # Test submission of form with invalid data
        response = self.client.post(
            reverse("account_signup"), {"email": "invalidemail"}
        )
        self.assertFalse(response.context["form"].is_valid())
        self.assertTemplateUsed(response, "account/signup.html")


class AuctionDetailViewTests(TestCase):
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

        # Login
        login_successful = self.client.login(
            username="testuser", password="12345"
        )
        self.assertTrue(
            login_successful, "User should be logged in for test cases."
        )

        # Create an artwork and an auction
        self.artwork = Artwork.objects.create(
            title="Test Artwork", description="Test Description"
        )
        self.auction = Auction.objects.create(
            artwork=self.artwork, reserve_price=100
        )

    def test_get_auction_detail(self):
        # Simulate logged in user
        self.client.login(username="testuser", password="12345")
        # Get response
        response = self.client.get(
            reverse(
                "auction_detail",
                kwargs={
                    "artwork_id": self.artwork.id,
                    "auction_id": self.auction.id,
                },
            )
        )
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "auction_detail.html")

    def test_ajax_request(self):
        # Simulate AJAX request
        response = self.client.get(
            reverse(
                "auction_detail",
                kwargs={
                    "artwork_id": self.artwork.id,
                    "auction_id": self.auction.id,
                },
            ),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        # Assert partial template used
        self.assertTemplateUsed(response, "auction_detail_partial.html")

    def test_post_bid_lower_than_reserve_price(self):
        response = self.client.post(
            reverse(
                "auction_detail",
                kwargs={
                    "artwork_id": self.artwork.id,
                    "auction_id": self.auction.id,
                },
            ),
            {"bid_amount": 50},
        )
        messages = list(get_messages(response.wsgi_request))
        self.assertGreater(
            len(messages), 0, "No messages were returned."
        )

        expected_error_message = (
            "Bid amount must be higher than the reserve price."
        )
        # Ensure the specific error message is in the messages
        self.assertTrue(
            any(
                expected_error_message in str(m).strip()
                for m in messages
            )
        )

    def test_post_valid_bid(self):
        # Post a valid bid
        valid_bid = self.auction.reserve_price + 10
        response = self.client.post(
            reverse(
                "auction_detail",
                kwargs={
                    "artwork_id": self.artwork.id,
                    "auction_id": self.auction.id,
                },
            ),
            {"bid_amount": valid_bid},
        )
        messages = list(get_messages(response.wsgi_request))
        self.assertGreater(
            len(messages), 0, "No messages were returned."
        )

        expected_success_message = (
            "My bid was submitted successfully!"
        )
        self.assertTrue(
            any(expected_success_message in str(m) for m in messages)
        )


class ProfileInfoViewTests(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(
            username="testuser", password="12345"
        )
        self.client.login(username="testuser", password="12345")

        # Create user profile with additional fields from the form
        self.profile = UserProfile.objects.create(
            user=self.user,
            name="Test Name",
            shipping_address="123 Test St, Test City, TS, Country, 12345",  # example data
        )

        # Create related objects like artwork, auction, and bid as needed
        self.artwork = Artwork.objects.create(
            title="Test Artwork", description="Test Description"
        )  # add fields
        self.auction = Auction.objects.create(
            artwork=self.artwork, reserve_price=100
        )  # add fields
        self.bid = Bids.objects.create(
            bidder=self.profile, auction=self.auction, amount=100
        )  # example bid

    def test_get_profile_info(self):
        # Use the actual name of the url pattern
        response = self.client.get(reverse("profile_info"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profile_info.html")

        # Assert that context contains profile and other details
        self.assertIn("profile", response.context)
        self.assertEqual(response.context["profile"], self.profile)
        self.assertIn("winning_bid_amount", response.context)


class UpdateProfileViewTests(TestCase):
    def setUp(self):
        self.username = "testuser"
        self.password = "12345"
        # Create a user
        self.user = User.objects.create_user(
            username=self.username, password=self.password
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            name="Original Name",
            shipping_address="Original Address",
        )

        # Login
        login_successful = self.client.login(
            username=self.username, password=self.password
        )
        self.assertTrue(
            login_successful, "User should be logged in for test cases."
        )

    def test_update_valid_field(self):
        url = reverse(
            "update_profile"
        )  # Use the actual name of the url pattern for UpdateProfileView
        field_to_update = "name"
        new_value = "New Name"

        response = self.client.post(
            url, {"field": field_to_update, "value": new_value}
        )

        # Reload profile from database
        self.profile.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.profile.name, new_value
        )  # Ensure the field was updated
        self.assertJSONEqual(
            str(response.content, encoding="utf8"),
            {
                "status": "success",
                "field": field_to_update,
                "new_value": new_value,
            },
        )

    def test_update_invalid_field(self):
        url = reverse(
            "update_profile"
        )  # Use the actual name of the url pattern for UpdateProfileView
        response = self.client.post(
            url, {"field": "invalid_field", "value": "Some Value"}
        )

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            str(response.content, encoding="utf8"),
            {"status": "error", "message": "Invalid field"},
        )


class PlaceBidViewTests(TestCase):
    def setUp(self):
        # Define user credentials
        self.username = "testuser"
        self.password = "12345"

        # Create a user and profile
        self.user = User.objects.create_user(
            username=self.username, password=self.password
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            name="Test User",
            shipping_address="123 Test St.",
        )

        # Login with the defined credentials
        logged_in = self.client.login(
            username=self.username, password=self.password
        )
        self.assertTrue(
            logged_in, "User should be logged in for test cases."
        )

        # Create an artwork and auction for testing
        self.artwork = Artwork.objects.create(
            title="Test Artwork",
            description="Test Description",
            category="Test",
            reserve_price=100,
        )
        self.auction = Auction.objects.create(
            artwork=self.artwork, status="active", reserve_price=100
        )

    def test_place_bid_successfully(self):
        """
        Test that a bid can be placed successfully through the AuctionDetailView
        and redirects to the ArtworkListView.
        """
        # Assuming I've setup self.user, self.auction, and self.artwork in setUp

        # Make a bid
        bid_amount = 150  # Ensure this is above the reserve price
        response = self.client.post(
            reverse(
                "auction_detail",
                kwargs={
                    "artwork_id": self.artwork.id,
                    "auction_id": self.auction.id,
                },
            ),
            {"bid_amount": bid_amount},
            follow=True,  # Follow the redirect after bid placement
        )
        # Capture and print messages for debugging
        messages = list(get_messages(response.wsgi_request))
        for message in messages:
            print(
                message
            )  # Debug: Print out what messages are being captured

        # Check if redirect URL in assertRedirects works
        self.assertRedirects(
            response,
            reverse(
                "auction_detail",
                kwargs={
                    "artwork_id": self.artwork.id,
                    "auction_id": self.auction.id,
                },
            ),
        )

        # Check if the bid was placed successfully
        self.assertTrue(
            self.auction.bids.filter(amount=bid_amount).exists()
        )

        # Capture and convert messages to string for comparison
        messages = [
            str(message)
            for message in get_messages(response.wsgi_request)
        ]

        # Now check if the desired message is in the list of message strings
        self.assertIn("My bid was submitted successfully!", messages)


class ActivityDashboardViewTests(TestCase):
    def setUp(self):
        # Create a user who will act as both artist and bidder
        self.user = User.objects.create_user(
            "user", "user@example.com", "userpassword"
        )
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            name="User",
            shipping_address="123 User St.",
        )

        self.artwork1 = Artwork.objects.create(
            artist=self.user_profile,
            title="First Artwork",
            description="First piece of art created by the user",
            category="Test",
            reserve_price=100,
            approval_status="approved",
        )

        self.artwork2 = Artwork.objects.create(
            artist=self.user_profile,
            title="Second Artwork",
            description="Second piece of art created by the user",
            category="Test",
            reserve_price=150,
            approval_status="approved",
        )

        # Create an active auction for the first artwork
        self.active_auction = Auction.objects.create(
            artwork=self.artwork1, status="active", reserve_price=100
        )

        # Create a closed auction for the second artwork
        self.closed_auction = Auction.objects.create(
            artwork=self.artwork2, status="closed", reserve_price=150
        )

        # Bidder activity: Create another user's artwork and auction for the original user to bid on
        self.other_artist_user = User.objects.create_user(
            "otherartist",
            "otherartist@example.com",
            "otherartistpassword",
        )
        self.other_artist_profile = UserProfile.objects.create(
            user=self.other_artist_user,
            name="Other Artist",
            shipping_address="456 Other Artist St.",
        )
        self.other_artwork = Artwork.objects.create(
            artist=self.other_artist_profile,
            title="Other Artist's Artwork",
            description="Created by another user",
            category="Other",
            reserve_price=200,
            approval_status="approved",
        )
        self.other_auction = Auction.objects.create(
            artwork=self.other_artwork,
            status="active",
            reserve_price=200,
        )

        # User places a bid on the other artist's auction
        self.bid_on_other_auction = Bids.objects.create(
            bidder=self.user_profile,  # User places a bid as a bidder
            auction=self.other_auction,
            amount=250,
        )

        # Log in the user
        self.client.login(username="user", password="userpassword")


def test_dashboard_view_with_auth(self):
    # Make a GET request to the dashboard view
    response = self.client.get(reverse("activity"))

    # Assert that the response is 200 OK.
    self.assertEqual(response.status_code, 200)

    # Assert that context contains the correct data
    self.assertIn("bidding_activity", response.context)
    self.assertIn("selling_activity", response.context)
    self.assertIn("active_auctions", response.context)
    self.assertIn("closed_auctions", response.context)

    # Assert the lengths of the context lists match expected values
    self.assertEqual(
        len(response.context["bidding_activity"]), 1
    )  # one bid by the user on another's auction
    self.assertEqual(
        len(response.context["selling_activity"]), 2
    )  # two artworks created by the user
    self.assertEqual(
        len(response.context["active_auctions"]), 1
    )  # one active auction for user's artwork
    self.assertEqual(
        len(response.context["closed_auctions"]), 1
    )  # one closed auction for user's artwork


def test_dashboard_view_no_data(self):
    self.bid_on_other_auction.delete()
    self.other_auction.delete()
    self.active_auction.delete()
    self.closed_auction.delete()
    self.other_artwork.delete()
    self.artwork1.delete()  # Delete both artworks
    self.artwork2.delete()
    # Make a GET request to the dashboard view
    response = self.client.get(reverse("activity"))

    # Assert that the response is 200 OK.
    self.assertEqual(response.status_code, 200)

    # Assert that context contains empty lists for activities and auctions
    self.assertEqual(len(response.context["bidding_activity"]), 0)
    self.assertEqual(len(response.context["selling_activity"]), 0)
    self.assertEqual(len(response.context["active_auctions"]), 0)
    self.assertEqual(len(response.context["closed_auctions"]), 0)


class AboutViewTest(TestCase):
    def test_about_view_template(self):
        # Get the URL for the about view
        url = reverse("about")

        # Use the test client to make a GET request to the view
        response = self.client.get(url)

        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is being used
        self.assertTemplateUsed(response, "about.html")


class SearchActiveAuctionArtworkViewTest(TestCase):
    def setUp(self):
        # Create an artwork and auction for testing
        self.artwork = Artwork.objects.create(
            title="Test Artwork",
            description="Test Description",
            category="Test",
            reserve_price=100,
            approval_status="approved",
        )
        self.auction = Auction.objects.create(
            artwork=self.artwork, status="active", reserve_price=100
        )

    def test_no_query(self):
        response = self.client.get(reverse("search_artworks"))
        print(response.content)
        self.assertContains(response, "Please enter a search term.")

    def test_no_results(self):
        response = self.client.get(
            reverse("search_artworks") + "?query=nonexistent"
        )
        # Assert the page_obj is empty or null

    def test_valid_query(self):
        # Insert Artworks that match the 'query'
        response = self.client.get(
            reverse("search_artworks") + "?query=matchingquery"
        )
        # Assert the page_obj contains the expected artworks

    def test_pagination(self):
        # Insert more than 10 matching Artworks
        response = self.client.get(
            reverse("search_artworks") + "?query=matchingquery&page=2"
        )
        # Assert page 2 has the correct artworks and the correct number of artworks


class ArtworkCreateFormTest(TestCase):
    def setUp(self):
        # Create a User instance
        self.test_user = User.objects.create_user(
            username="testuser", password="12345"
        )

        # Create a UserProfile instance
        self.user_profile = UserProfile.objects.create(
            user=self.test_user,
            name="Test User",
            shipping_address="123 Test St, Test City",
            create_date=timezone.now(),
        )

    def test_form_initialization(self):
        form = ArtworkCreateForm()
        self.assertIn("title", form.fields)
        self.assertIn("image", form.fields)
        # Add more assertions if I want to test the presence of other fields

    def test_clean_method(self):
        form_data = {
            "title": "Test Artwork",
            "description": "A test description",
            "category": "painting",
            "reserve_price": "100.00",
            "auction_duration": 5,
            # other fields as necessary
        }
        image_file = SimpleUploadedFile(
            "test_image.jpg",
            b"image_content",
            content_type="image/jpeg",
        )

        form = ArtworkCreateForm(
            data=form_data, files={"image": image_file}
        )

        if not form.is_valid():
            print(
                "Validation errors in test_clean_method:", form.errors
            )
            self.fail("Form did not validate with provided data.")
        else:
            # Access cleaned_data directly from the form after checking is_valid
            self.assertEqual(
                form.cleaned_data.get("title"), "Test Artwork"
            )

    @patch(
        "uptowngallery.forms.cloudinary.uploader.upload"
    )  # Adjust with the actual import path
    def test_save_method(self, mock_upload):
        mock_upload.return_value = {
            "url": "http://example.com/test.jpg"
        }

        image_file = SimpleUploadedFile(
            "test_image.jpg",
            b"image_content",
            content_type="image/jpeg",
        )
        form_data = {
            "title": "Test Artwork",
            "description": "A test description",
            "category": "painting",
            "reserve_price": "100.00",
            "auction_duration": 5,  # Ensure this is an acceptable value for the form
        }

        form = ArtworkCreateForm(
            data=form_data, files={"image": image_file}
        )  # Image is passed as part of files

        if not form.is_valid():
            print("Validation errors in test_save_method:", form.errors)
            self.fail("Form did not validate with provided data.")
        else:
            artwork = form.save(commit=False)
            # Assuming form is valid and save operations here
            # Remember to implement assertions and any necessary cleanup or additional operations
            artwork.image_url = mock_upload.return_value.get("url")
