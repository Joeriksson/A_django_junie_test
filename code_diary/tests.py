import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from .models import DiaryEntry, UserProfile
from datetime import date

# Model tests
class TestDiaryEntryModel(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.entry = DiaryEntry.objects.create(
            user=self.user,
            date=date(2023, 5, 15),
            title="Test Entry",
            content="This is a test entry content.",
            technologies="Python, Django, pytest"
        )

    def test_diary_entry_creation(self):
        """Test that a diary entry can be created with the expected values."""
        self.assertEqual(self.entry.title, "Test Entry")
        self.assertEqual(self.entry.content, "This is a test entry content.")
        self.assertEqual(self.entry.technologies, "Python, Django, pytest")
        self.assertEqual(self.entry.date, date(2023, 5, 15))

    def test_diary_entry_str_representation(self):
        """Test the string representation of a diary entry."""
        expected_str = f"{self.entry.date}: Test Entry"
        self.assertEqual(str(self.entry), expected_str)

    def test_diary_entry_ordering(self):
        """Test that diary entries are ordered by date in descending order."""
        DiaryEntry.objects.create(
            user=self.user,
            date=date(2023, 5, 16),
            title="Newer Entry",
            content="This is a newer entry.",
            technologies="Python, Django"
        )
        DiaryEntry.objects.create(
            user=self.user,
            date=date(2023, 5, 14),
            title="Older Entry",
            content="This is an older entry.",
            technologies="Python, Django"
        )

        entries = DiaryEntry.objects.all()
        self.assertEqual(entries[0].title, "Newer Entry")
        self.assertEqual(entries[1].title, "Test Entry")
        self.assertEqual(entries[2].title, "Older Entry")

# View tests
@pytest.mark.django_db
class TestDiaryEntryViews:
    def setup_method(self):
        self.client = Client()
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.entry = DiaryEntry.objects.create(
            user=self.user,
            date=date(2023, 5, 15),
            title="Test Entry",
            content="This is a test entry content.",
            technologies="Python, Django, pytest"
        )
        self.list_url = reverse('code_diary:my_entries')
        self.detail_url = reverse('code_diary:entry_detail', args=[self.entry.pk])
        self.create_url = reverse('code_diary:entry_create')
        self.update_url = reverse('code_diary:entry_update', args=[self.entry.pk])
        self.delete_url = reverse('code_diary:entry_delete', args=[self.entry.pk])

    def login(self):
        """Helper method to log in the test user."""
        self.client.login(username='testuser', password='testpassword')

    def test_entry_list_view(self):
        """Test that the entry list view returns a 200 status code when logged in."""
        # Log in the user
        self.login()
        response = self.client.get(self.list_url)
        assert response.status_code == 200
        assert 'entries' in response.context
        assert len(response.context['entries']) == 1

    def test_entry_detail_view(self):
        """Test that the entry detail view returns a 200 status code."""
        response = self.client.get(self.detail_url)
        assert response.status_code == 200
        assert response.context['entry'] == self.entry

    def test_entry_create_view_get(self):
        """Test that the entry create view returns a 200 status code when logged in."""
        # Log in the user
        self.login()
        response = self.client.get(self.create_url)
        assert response.status_code == 200
        assert 'form' in response.context

    def test_entry_create_view_get_redirect_if_not_logged_in(self):
        """Test that the entry create view redirects to login page if not logged in."""
        response = self.client.get(self.create_url)
        assert response.status_code == 302
        assert reverse('code_diary:login') in response.url

    def test_entry_create_view_post(self):
        """Test that a new entry can be created when logged in."""
        # Log in the user
        self.login()
        entry_count = DiaryEntry.objects.count()
        response = self.client.post(self.create_url, {
            'date': '2023-05-20',
            'title': 'New Test Entry',
            'content': 'This is a new test entry content.',
            'technologies': 'Python, Django, pytest'
        })
        assert response.status_code == 302  # Redirect after successful creation
        assert DiaryEntry.objects.count() == entry_count + 1
        assert DiaryEntry.objects.filter(title='New Test Entry').exists()

    def test_entry_create_view_post_redirect_if_not_logged_in(self):
        """Test that the entry create view post redirects to login page if not logged in."""
        entry_count = DiaryEntry.objects.count()
        response = self.client.post(self.create_url, {
            'date': '2023-05-20',
            'title': 'New Test Entry',
            'content': 'This is a new test entry content.',
            'technologies': 'Python, Django, pytest'
        })
        assert response.status_code == 302
        assert reverse('code_diary:login') in response.url
        assert DiaryEntry.objects.count() == entry_count  # No new entry created

    def test_entry_update_view_get(self):
        """Test that the entry update view returns a 200 status code when logged in."""
        # Log in the user
        self.login()
        response = self.client.get(self.update_url)
        assert response.status_code == 200
        assert 'form' in response.context

    def test_entry_update_view_get_redirect_if_not_logged_in(self):
        """Test that the entry update view redirects to login page if not logged in."""
        response = self.client.get(self.update_url)
        assert response.status_code == 302
        assert reverse('code_diary:login') in response.url

    def test_entry_update_view_post(self):
        """Test that an entry can be updated when logged in."""
        # Log in the user
        self.login()
        response = self.client.post(self.update_url, {
            'date': '2023-05-15',
            'title': 'Updated Test Entry',
            'content': 'This is an updated test entry content.',
            'technologies': 'Python, Django, pytest, Updated'
        })
        assert response.status_code == 302  # Redirect after successful update
        self.entry.refresh_from_db()
        assert self.entry.title == 'Updated Test Entry'
        assert self.entry.content == 'This is an updated test entry content.'
        assert self.entry.technologies == 'Python, Django, pytest, Updated'

    def test_entry_update_view_post_redirect_if_not_logged_in(self):
        """Test that the entry update view post redirects to login page if not logged in."""
        response = self.client.post(self.update_url, {
            'date': '2023-05-15',
            'title': 'Updated Test Entry',
            'content': 'This is an updated test entry content.',
            'technologies': 'Python, Django, pytest, Updated'
        })
        assert response.status_code == 302
        assert reverse('code_diary:login') in response.url
        self.entry.refresh_from_db()
        assert self.entry.title != 'Updated Test Entry'  # Entry not updated

    def test_entry_delete_view_get(self):
        """Test that the entry delete view returns a 200 status code when logged in."""
        # Log in the user
        self.login()
        response = self.client.get(self.delete_url)
        assert response.status_code == 200

    def test_entry_delete_view_get_redirect_if_not_logged_in(self):
        """Test that the entry delete view redirects to login page if not logged in."""
        response = self.client.get(self.delete_url)
        assert response.status_code == 302
        assert reverse('code_diary:login') in response.url

    def test_entry_delete_view_post(self):
        """Test that an entry can be deleted when logged in."""
        # Log in the user
        self.login()
        entry_count = DiaryEntry.objects.count()
        response = self.client.post(self.delete_url)
        assert response.status_code == 302  # Redirect after successful deletion
        assert DiaryEntry.objects.count() == entry_count - 1
        assert not DiaryEntry.objects.filter(pk=self.entry.pk).exists()

    def test_entry_delete_view_post_redirect_if_not_logged_in(self):
        """Test that the entry delete view post redirects to login page if not logged in."""
        entry_count = DiaryEntry.objects.count()
        response = self.client.post(self.delete_url)
        assert response.status_code == 302
        assert reverse('code_diary:login') in response.url
        assert DiaryEntry.objects.count() == entry_count  # Entry not deleted


@pytest.mark.django_db
class TestAuthViews:
    """Tests for authentication views (login, signup, logout)."""

    def setup_method(self):
        self.client = Client()
        self.login_url = reverse('code_diary:login')
        self.signup_url = reverse('code_diary:signup')
        self.logout_url = reverse('code_diary:logout')
        self.home_url = reverse('code_diary:home')

        # Create a test user
        self.user = User.objects.create_user(
            username='authuser',
            email='auth@example.com',
            password='authpassword'
        )

    def test_login_view_get(self):
        """Test that the login view returns a 200 status code."""
        response = self.client.get(self.login_url)
        assert response.status_code == 200
        assert 'form' in response.context

    def test_login_view_post_valid(self):
        """Test that a valid login redirects to the success URL."""
        response = self.client.post(self.login_url, {
            'username': 'authuser',
            'password': 'authpassword'
        })
        assert response.status_code == 302
        assert reverse('code_diary:my_entries') in response.url

        # Check that the user is logged in
        response = self.client.get(self.home_url)
        assert response.context['user'].is_authenticated

    def test_login_view_post_invalid(self):
        """Test that an invalid login returns to the login page with an error."""
        response = self.client.post(self.login_url, {
            'username': 'authuser',
            'password': 'wrongpassword'
        })
        assert response.status_code == 200
        assert 'form' in response.context
        assert response.context['form'].errors

        # Check that the user is not logged in
        response = self.client.get(self.home_url)
        assert not response.context['user'].is_authenticated

    def test_signup_view_get(self):
        """Test that the signup view returns a 200 status code."""
        response = self.client.get(self.signup_url)
        assert response.status_code == 200
        assert 'form' in response.context

    def test_signup_view_post_valid(self):
        """Test that a valid signup creates a new user and redirects to the login page."""
        user_count = User.objects.count()
        response = self.client.post(self.signup_url, {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'newpassword123',
            'password2': 'newpassword123'
        })
        assert response.status_code == 302
        assert reverse('code_diary:login') in response.url
        assert User.objects.count() == user_count + 1
        assert User.objects.filter(username='newuser').exists()

        # Check that the user has a profile
        new_user = User.objects.get(username='newuser')
        assert hasattr(new_user, 'profile')
        assert isinstance(new_user.profile, UserProfile)

    def test_signup_view_post_invalid(self):
        """Test that an invalid signup returns to the signup page with an error."""
        user_count = User.objects.count()
        response = self.client.post(self.signup_url, {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'newpassword123',
            'password2': 'differentpassword'
        })
        assert response.status_code == 200
        assert 'form' in response.context
        assert response.context['form'].errors
        assert User.objects.count() == user_count

    def test_logout_view(self):
        """Test that the logout view logs out the user and redirects to the home page."""
        # Log in the user
        self.client.login(username='authuser', password='authpassword')

        # Check that the user is logged in
        response = self.client.get(self.home_url)
        assert response.context['user'].is_authenticated

        # Log out the user
        response = self.client.get(self.logout_url)
        assert response.status_code == 200
        assert 'Logged Out' in str(response.content)

        # Check that the user is logged out
        response = self.client.get(self.home_url)
        assert not response.context['user'].is_authenticated
