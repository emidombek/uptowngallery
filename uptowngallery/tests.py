from datetime import timedelta
from unittest.mock import patch
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.auth.models import (
    User,
)
from django.contrib.messages import get_messages
from django.contrib.sessions.middleware import SessionMiddleware
from django.core import mail
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, RequestFactory, Client
from django.test.utils import override_settings
from django.urls import reverse
from django.utils import timezone
from .admin import ArtworkAdmin
from .forms import CustomSignupForm, ArtworkCreateForm, BidForm
from .models import Artwork, UserProfile, Auction, Bids
from .signals import user_signed_up, auction_closed, bid_placed


class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="12345"
        )
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
        self.assertAlmostEqual(
            self.user_profile.create_date,
            timezone.now(),
            delta=timedelta(seconds=30),
        )

    def test_one_to_one_relationship_with_user(self):
        with self.assertRaises(Exception):
            UserProfile.objects.create(
                user=self.user, name="Another Test User"
            )


class ArtworkModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="12345"
        )
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            name="Test User",
            shipping_address="123 Test Street",
        )
        self.artwork = Artwork.objects.create(
            artist=self.user_profile,
            title="Test Artwork",
            description="A test description",
            category="painting",
            reserve_price=100.00,
        )

    def test_artwork_creation(self):
        self.assertEqual(self.artwork.title, "Test Artwork")
        self.assertEqual(self.artwork.artist, self.user_profile)
        self.assertEqual(self.artwork.description, "A test description")
        self.assertEqual(self.artwork.category, "painting")
        self.assertEqual(self.artwork.reserve_price, 100.00)

    def test_string_representation(self):
        expected_string = f"Artwork #{self.artwork.id} - Title: {self.artwork.title} - Artist: {self.artwork.artist}"
        self.assertEqual(str(self.artwork), expected_string)

    def test_calculate_price(self):
        self.assertEqual(self.artwork.calculate_price(), 100.00)
        auction = Auction.objects.create(
            artwork=self.artwork, status="active", reserve_price=100.00
        )
        self.assertEqual(self.artwork.calculate_price(), 100.00)
        bid1 = Bids.objects.create(auction=auction, amount=150)
        bid2 = Bids.objects.create(auction=auction, amount=200)
        self.assertEqual(self.artwork.calculate_price(), 200)

    def test_approve_and_start_auction_creates_auction_after_admin_approval(
        self,
    ):
        self.artwork.approval_status = "approved"
        self.artwork.save()
        self.assertEqual(self.artwork.approval_status, "approved")
        self.artwork.approve_and_start_auction()
        self.artwork.refresh_from_db()
        self.assertEqual(self.artwork.approval_status, "approved")
        auction = Auction.objects.filter(artwork=self.artwork).first()
        self.assertIsNotNone(auction, "Auction should be created")
        self.assertTrue(auction.is_active)
        self.assertEqual(auction.status, "active")


class AuctionModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass"
        )
        self.admin_user = User.objects.create_superuser(
            username="adminuser", password="adminpass"
        )
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            name="Test Artist",
            shipping_address="123 Street",
        )
        self.artwork = Artwork.objects.create(
            artist=self.user_profile,
            title="Test Artwork",
            description="A beautiful artwork",
            category="painting",
            reserve_price=100.00,
        )

    def test_artwork_approval_triggers_auction_creation(self):
        self.client.login(username="adminuser", password="adminpass")
        self.artwork.approval_status = "approved"
        self.artwork.save()
        self.assertTrue(self.artwork.auctions.exists())
        auction = self.artwork.auctions.first()
        self.assertIsNotNone(auction)
        self.assertEqual(auction.status, "active")

    def test_calculate_auction_end_date(self):
        auction_start = timezone.now().replace(microsecond=0)
        durations = {
            "3_days": timedelta(days=3),
            "5_days": timedelta(days=5),
            "7_days": timedelta(days=7),
        }
        for duration_key, duration_value in durations.items():
            self.artwork.auction_duration = duration_key
            calculated_end_date = (
                self.artwork.calculate_auction_end_date(
                    auction_start
                ).replace(microsecond=0)
            )
            expected_end_date = auction_start + duration_value
            delta_seconds = abs(
                (
                    calculated_end_date - expected_end_date
                ).total_seconds()
            )
            self.assertTrue(
                delta_seconds < 1,
                f"Auction end date calculation failed for {duration_key} with delta {delta_seconds} seconds",
            )

    def test_artwork_denial(self):
        self.client.login(username="adminuser", password="adminpass")
        self.artwork.approval_status = "rejected"
        self.artwork.save()
        self.assertEqual(self.artwork.approval_status, "rejected")

    def test_auction_closure(self):
        self.artwork.approval_status = "approved"
        self.artwork.save()
        auction = self.artwork.auctions.first()
        with patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = auction.end_date + timedelta(
                minutes=1
            )
            auction.status = "closed"
            auction.save()
        updated_auction = Auction.objects.get(id=auction.id)
        self.assertEqual(updated_auction.status, "closed")

    def tearDown(self):
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
        )

        self.auction = Auction.objects.create(
            artwork=self.artwork,
            status="active",
            reserve_price=100,
        )

    def test_create_valid_bid(self):
        bid = Bids.objects.create(
            bidder=self.user_profile,
            auction=self.auction,
            amount=150,
        )
        self.assertEqual(Bids.objects.count(), 1)
        self.assertEqual(bid.amount, 150)
        self.assertEqual(bid.bidder, self.user_profile)
        self.assertEqual(bid.auction, self.auction)

    def test_negative_bid_amount(self):
        with self.assertRaises(ValidationError):
            Bids.objects.create(
                bidder=self.user_profile,
                auction=self.auction,
                amount=-50,
            ).clean()

    def test_bid_time_auto_set(self):
        bid = Bids.objects.create(
            bidder=self.user_profile,
            auction=self.auction,
            amount=200,
        )
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
        self.assertTrue("recent_artworks" in response.context)


class ArtworkListViewTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(
            username="testuser", password="12345"
        )
        self.artwork1 = Artwork.objects.create(
            title="Artwork 1",
            description="Description 1",
            image="path/to/image1.jpg",
            category="painting",
            reserve_price=100.00,
            auction_duration=3,
            approval_status="approved",
        )
        self.auction1 = Auction.objects.create(
            artwork=self.artwork1,
            status="active",
        )
        self.artwork2 = Artwork.objects.create(
            title="Artwork 2",
            description="Description 2",
            image="path/to/image2.jpg",
            category="sculpture",
            reserve_price=200.00,
            auction_duration=4,
            approval_status="approved",
        )
        self.auction2 = Auction.objects.create(
            artwork=self.artwork2,
            status="active",
        )

    def test_artwork_list_loads_correctly(self):
        response = self.client.get(reverse("artwork_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "artwork_list.html")
        self.assertTrue("page_obj" in response.context)

    def test_artwork_list_filter_by_category(self):
        category_to_filter = "painting"
        response = self.client.get(
            reverse("artwork_list"), {"category": category_to_filter}
        )
        self.assertEqual(response.status_code, 200)
        artworks_in_context = response.context["page_obj"].object_list
        for artwork in artworks_in_context:
            self.assertEqual(artwork.category, category_to_filter)
        expected_count = Artwork.objects.filter(
            category=category_to_filter
        ).count()
        self.assertEqual(len(artworks_in_context), expected_count)


class CreateArtworkViewTests(TestCase):
    def setUp(self):
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
        post_data = {
            "title": "New Artwork",
            "description": "Beautiful Artwork",
            "image": "image/upload/path.jpg",
            "category": "painting",
            "reserve_price": 100.00,
            "auction_duration": "3",
        }
        response = self.client.post(
            reverse("create_artwork"), post_data
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Artwork.objects.filter(title="New Artwork").exists()
        )

    def test_create_artwork_without_login(self):
        self.client.logout()
        post_data = {
            "title": "New Artwork",
            "description": "Beautiful Artwork",
            "image": "image/upload/path.jpg",
            "category": "painting",
            "reserve_price": 100.00,
            "auction_duration": "3",
        }
        response = self.client.post(
            reverse("create_artwork"), post_data
        )
        self.assertNotEqual(response.status_code, 200)
        self.assertFalse(
            Artwork.objects.filter(title="New Artwork").exists()
        )


class PendingArtworksViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="12345"
        )
        self.profile = UserProfile.objects.create(user=self.user)
        self.client.login(username="testuser", password="12345")
        for i in range(15):
            Artwork.objects.create(
                artist=self.profile,
                title=f"Artwork {i}",
                approved=False,
            )

    def test_pending_artworks_display(self):
        response = self.client.get(reverse("pending_artworks"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pending_artworks.html")
        artworks_in_context = response.context["artworks"]
        self.assertTrue(
            all(
                artwork.approved == False
                for artwork in artworks_in_context
            )
        )
        self.assertTrue(len(artworks_in_context) <= 10)

    def test_pagination(self):
        response = self.client.get(
            reverse("pending_artworks") + "?page=1"
        )
        self.assertEqual(len(response.context["artworks"]), 10)
        response = self.client.get(
            reverse("pending_artworks") + "?page=2"
        )
        self.assertTrue(len(response.context["artworks"]) > 0)

    def test_access_control(self):
        self.client.logout()
        response = self.client.get(reverse("pending_artworks"))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            response.url.startswith(reverse("account_login"))
        )

    def test_empty_page_redirection(self):
        response = self.client.get(
            reverse("pending_artworks") + "?page=100"
        )
        artworks_in_context = response.context["artworks"]
        self.assertEqual(len(artworks_in_context), 5)
        self.assertEqual(artworks_in_context.number, 2)


class CustomSignupViewTests(TestCase):
    def test_get_signup_page(self):
        response = self.client.get(reverse("account_signup"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "signup_template.html")
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
            reverse("account_signup"), form_data, follow=True
        )
        self.assertEqual(response.status_code, 200)
        user = (
            get_user_model()
            .objects.filter(email="user@example.com")
            .first()
        )
        self.assertIsNotNone(user, "User was not created")
        try:
            profile = UserProfile.objects.get(user=user)
            self.assertEqual(
                profile.shipping_address,
                "123 Test St, Testville, Testland, US, 12345",
            )
        except UserProfile.DoesNotExist:
            self.fail("UserProfile was not created for the new user")

    def test_form_validation(self):
        response = self.client.post(
            reverse("account_signup"),
            {"email": "invalidemail"},
        )
        self.assertFalse(response.context["form"].is_valid())
        self.assertTemplateUsed(response, "account/signup.html")

        response = self.client.get(reverse("account_signup"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/signup.html")
        self.assertIsInstance(
            response.context.get("form"), CustomSignupForm
        )


class AuctionDetailViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="12345"
        )
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            name="Test User",
            shipping_address="123 Test St",
        )
        login_successful = self.client.login(
            username="testuser", password="12345"
        )
        self.assertTrue(
            login_successful, "User should be logged in for test cases."
        )
        self.artwork = Artwork.objects.create(
            title="Test Artwork", description="Test Description"
        )
        self.auction = Auction.objects.create(
            artwork=self.artwork, reserve_price=100
        )
        valid_bid_amount = 100
        bid = Bids.objects.create(
            auction=self.auction,
            bidder=self.user_profile,
            amount=valid_bid_amount,
            bid_time=timezone.now(),
        )

    def test_get_auction_detail(self):
        response = self.client.get(
            reverse(
                "auction_detail",
                kwargs={
                    "artwork_id": self.artwork.id,
                    "auction_id": self.auction.id,
                },
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "auction_detail.html")

    def test_get_auction_detail_partial(self):
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
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "auction_detail_partial.html")


class ProfileInfoViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="12345"
        )
        self.client.login(username="testuser", password="12345")
        self.profile = UserProfile.objects.create(
            user=self.user,
            name="Test Name",
            shipping_address="123 Test St, Test City, TS, Country, 12345",
        )
        self.artwork = Artwork.objects.create(
            title="Test Artwork", description="Test Description"
        )
        self.auction = Auction.objects.create(
            artwork=self.artwork, reserve_price=100
        )
        self.bid = Bids.objects.create(
            bidder=self.profile, auction=self.auction, amount=100
        )

    def test_get_profile_info(self):
        response = self.client.get(reverse("profile_info"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profile_info.html")
        self.assertIn("profile", response.context)
        self.assertEqual(response.context["profile"], self.profile)
        self.assertIn("winning_bid_amount", response.context)


class UpdateProfileViewTests(TestCase):
    def setUp(self):
        self.username = "testuser"
        self.password = "12345"
        self.user = User.objects.create_user(
            username=self.username, password=self.password
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            name="Original Name",
            shipping_address="Original Address",
        )
        login_successful = self.client.login(
            username=self.username, password=self.password
        )
        self.assertTrue(
            login_successful, "User should be logged in for test cases."
        )

    def test_update_valid_field(self):
        url = reverse("update_profile")
        field_to_update = "name"
        new_value = "New Name"
        response = self.client.post(
            url, {"field": field_to_update, "value": new_value}
        )
        self.profile.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.profile.name, new_value)
        self.assertJSONEqual(
            str(response.content, encoding="utf8"),
            {
                "status": "success",
                "field": field_to_update,
                "new_value": new_value,
            },
        )

    def test_update_invalid_field(self):
        url = reverse("update_profile")
        response = self.client.post(
            url, {"field": "invalid_field", "value": "Some Value"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            str(response.content, encoding="utf8"),
            {"status": "error", "message": "Invalid field"},
        )


class ActivityDashboardViewTests(TestCase):
    def setUp(self):
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
        self.active_auction = Auction.objects.create(
            artwork=self.artwork1, status="active", reserve_price=100
        )
        self.closed_auction = Auction.objects.create(
            artwork=self.artwork2, status="closed", reserve_price=150
        )
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
        self.bid_on_other_auction = Bids.objects.create(
            bidder=self.user_profile,
            auction=self.other_auction,
            amount=250,
        )
        self.client.login(username="user", password="userpassword")


def test_dashboard_view_with_auth(self):
    response = self.client.get(reverse("activity"))
    self.assertEqual(response.status_code, 200)
    self.assertIn("bidding_activity", response.context)
    self.assertIn("selling_activity", response.context)
    self.assertIn("active_auctions", response.context)
    self.assertIn("closed_auctions", response.context)
    self.assertEqual(len(response.context["bidding_activity"]), 1)
    self.assertEqual(len(response.context["selling_activity"]), 2)
    self.assertEqual(len(response.context["active_auctions"]), 1)
    self.assertEqual(len(response.context["closed_auctions"]), 1)


def test_dashboard_view_no_data(self):
    self.bid_on_other_auction.delete()
    self.other_auction.delete()
    self.active_auction.delete()
    self.closed_auction.delete()
    self.other_artwork.delete()
    self.artwork1.delete()
    self.artwork2.delete()
    response = self.client.get(reverse("activity"))
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(response.context["bidding_activity"]), 0)
    self.assertEqual(len(response.context["selling_activity"]), 0)
    self.assertEqual(len(response.context["active_auctions"]), 0)
    self.assertEqual(len(response.context["closed_auctions"]), 0)


class AboutViewTest(TestCase):
    def test_about_view_template(self):
        url = reverse("about")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "about.html")


class SearchActiveAuctionArtworkViewTest(TestCase):
    def setUp(self):
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

    def test_valid_query(self):
        response = self.client.get(
            reverse("search_artworks") + "?query=matchingquery"
        )

    def test_pagination(self):
        response = self.client.get(
            reverse("search_artworks") + "?query=matchingquery&page=2"
        )


class ArtworkCreateFormTest(TestCase):
    def setUp(self):
        self.test_user = User.objects.create_user(
            username="testuser", password="12345"
        )
        self.user_profile = UserProfile.objects.create(
            user=self.test_user,
            name="Test User",
            shipping_address="123 Test St, Test City",
            create_date=timezone.now(),
        )
        login_successful = self.client.login(
            username="testuser", password="12345"
        )
        self.assertTrue(
            login_successful, "User should be logged in for test cases."
        )

    def test_form_initialization(self):
        form = ArtworkCreateForm()
        self.assertIn("title", form.fields)
        self.assertIn("image", form.fields)

    def test_clean_method(self):
        form_data = {
            "title": "Test Artwork",
            "description": "A test description",
            "category": "painting",
            "reserve_price": "100.00",
            "auction_duration": 5,
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
            self.assertEqual(
                form.cleaned_data.get("title"), "Test Artwork"
            )

    def test_create_artwork_invalid_form(self):
        response = self.client.post(
            reverse("create_artwork"),
            {
                "title": "",
                "description": "",
                "category": "",
                "reserve_price": "",
                "auction_duration": 5,
            },
            follow=True,
        )
        print("Redirection:", response.redirect_chain)
        print(
            "Form Errors:",
            response.context["form"].errors
            if "form" in response.context
            else "No form in context",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "create_artwork.html")
        self.assertTrue("form" in response.context)
        self.assertFalse(response.context["form"].is_valid())
        self.assertTrue(response.context["form"].errors)

    @patch("uptowngallery.forms.cloudinary.uploader.upload")
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
            "auction_duration": 5,
        }
        form = ArtworkCreateForm(
            data=form_data, files={"image": image_file}
        )
        if not form.is_valid():
            print("Validation errors in test_save_method:", form.errors)
            self.fail("Form did not validate with provided data.")
        else:
            artwork = form.save(commit=False)
            artwork.image_url = mock_upload.return_value.get("url")


class CustomSignupFormTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )

    def test_form_initialization(self):
        form = CustomSignupForm()
        self.assertIn("name", form.fields)
        self.assertIn("street_address", form.fields)
        self.assertIn("city", form.fields)
        self.assertIn("state", form.fields)
        self.assertIn("country", form.fields)
        self.assertIn("zipcode", form.fields)

    def test_valid_data(self):
        form_data = {
            "email": "user@example.com",
            "password1": "complexpassword",
            "password2": "complexpassword",
            "name": "Test User",
            "street_address": "123 Test St",
            "city": "Test City",
            "state": "Test State",
            "country": "US",
            "zipcode": "12345",
        }
        form = CustomSignupForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_data(self):
        form_data = {
            "email": "user@example.com",
            "password1": "complexpassword",
            "password2": "complexpassword",
            "street_address": "123 Test St",
            "city": "Test City",
            "state": "Test State",
            "country": "US",
            "zipcode": "12345",
        }
        form = CustomSignupForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_save_method(self):
        form_data = {
            "email": "user@example.com",
            "password1": "complexpassword",
            "password2": "complexpassword",
            "name": "Test User",
            "street_address": "123 Test St",
            "city": "Test City",
            "state": "Test State",
            "country": "US",
            "zipcode": "12345",
        }
        form = CustomSignupForm(data=form_data)
        request = self.factory.post("/signup/")
        request.user = self.user
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        if form.is_valid():
            user = form.save(request)
            profile, created = UserProfile.objects.get_or_create(
                user=user
            )
            self.assertEqual(
                profile.shipping_address,
                "123 Test St, Test City, Test State, US, 12345",
            )
        else:
            self.fail("Form did not validate with provided data")


class MockRequest:
    def __init__(self, user):
        self.user = user


class ArtworkAdminTest(TestCase):
    def setUp(self):
        self.artwork_admin = ArtworkAdmin(
            model=Artwork, admin_site=AdminSite()
        )
        self.user = User.objects.create_user(
            username="admin", password="password"
        )
        self.artist_user = User.objects.create_user(
            username="artist",
            password="password",
            email="artist@example.com",
        )
        self.artist_profile = UserProfile.objects.create(
            user=self.artist_user,
        )
        self.artwork = Artwork.objects.create(
            title="Test Artwork",
            artist=self.artist_profile,
        )

    def test_list_display(self):
        self.assertEqual(
            self.artwork_admin.list_display,
            (
                "artist",
                "approved",
                "auction_start",
                "create_date",
                "description",
                "image",
            ),
        )

    def test_list_filter(self):
        self.assertEqual(
            self.artwork_admin.list_filter,
            ("approved",),
        )

    def get_form(self, request, obj=None, **kwargs):
        if request.user.groups.filter(name="Artist").exists():
            return ArtworkCreateForm
        return super().get_form(request, obj, **kwargs)

    def test_approve_artworks(self):
        request = MockRequest(user=self.user)
        self.artwork_admin.approve_artworks(
            request, Artwork.objects.filter(id=self.artwork.id)
        )
        updated_artwork = Artwork.objects.get(id=self.artwork.id)
        self.assertTrue(updated_artwork.approved)

    def test_delete_queryset(self):
        artwork2 = Artwork.objects.create(title="Another Test Artwork")
        request = MockRequest(user=self.user)
        self.artwork_admin.delete_queryset(
            request, Artwork.objects.all()
        )
        self.assertEqual(Artwork.objects.count(), 0)

    def test_delete_model(self):
        request = MockRequest(user=self.user)
        self.artwork_admin.delete_model(request, self.artwork)
        self.assertEqual(Artwork.objects.count(), 0)

    @patch("django.core.mail.send_mail")
    def test_approve_artworks_and_email(self, mock_send_mail):
        mail.outbox.clear()
        request = MockRequest(user=self.user)
        self.artwork_admin.approve_artworks(
            request, Artwork.objects.filter(id=self.artwork.id)
        )
        updated_artwork = Artwork.objects.get(id=self.artwork.id)
        self.assertTrue(updated_artwork.approved)
        self.assertEqual(len(mail.outbox), 1)
        sent_mail = mail.outbox[0]
        self.assertEqual(
            sent_mail.subject, "Your Artwork Has Been Approved!"
        )
        self.assertIn(
            'Your artwork "{}" has been approved and your auction has started.'.format(
                updated_artwork.title
            ),
            sent_mail.body,
        )
        self.assertEqual(
            sent_mail.from_email, "mailto@uptowngallery.com"
        )
        self.assertEqual(
            sent_mail.recipients(), [updated_artwork.artist.user.email]
        )

    @patch("django.core.mail.send_mail")
    def test_deny_artworks_and_email(self, mock_send_mail):
        mail.outbox.clear()
        request = MockRequest(user=self.user)
        self.artwork_admin.deny_artworks(
            request, Artwork.objects.filter(id=self.artwork.id)
        )
        updated_artwork = Artwork.objects.get(id=self.artwork.id)
        self.assertFalse(updated_artwork.approved)
        self.assertEqual(len(mail.outbox), 1)
        sent_mail = mail.outbox[0]
        self.assertEqual(
            sent_mail.subject, "Your Artwork Has Been Denied"
        )
        self.assertIn(
            'Unfortunately, your artwork "{}" has been denied and will be deleted.'.format(
                updated_artwork.title
            ),
            sent_mail.body,
        )
        self.assertEqual(
            sent_mail.from_email, "mailto@uptowngallery.com"
        )
        self.assertEqual(
            sent_mail.recipients(), [updated_artwork.artist.user.email]
        )
