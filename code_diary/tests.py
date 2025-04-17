import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from .models import DiaryEntry
from datetime import date

# Model tests
class TestDiaryEntryModel(TestCase):
    def setUp(self):
        self.entry = DiaryEntry.objects.create(
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
            date=date(2023, 5, 16),
            title="Newer Entry",
            content="This is a newer entry.",
            technologies="Python, Django"
        )
        DiaryEntry.objects.create(
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
        self.entry = DiaryEntry.objects.create(
            date=date(2023, 5, 15),
            title="Test Entry",
            content="This is a test entry content.",
            technologies="Python, Django, pytest"
        )
        self.list_url = reverse('code_diary:entry_list')
        self.detail_url = reverse('code_diary:entry_detail', args=[self.entry.pk])
        self.create_url = reverse('code_diary:entry_create')
        self.update_url = reverse('code_diary:entry_update', args=[self.entry.pk])
        self.delete_url = reverse('code_diary:entry_delete', args=[self.entry.pk])

    def test_entry_list_view(self):
        """Test that the entry list view returns a 200 status code."""
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
        """Test that the entry create view returns a 200 status code."""
        response = self.client.get(self.create_url)
        assert response.status_code == 200
        assert 'form' in response.context

    def test_entry_create_view_post(self):
        """Test that a new entry can be created."""
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

    def test_entry_update_view_get(self):
        """Test that the entry update view returns a 200 status code."""
        response = self.client.get(self.update_url)
        assert response.status_code == 200
        assert 'form' in response.context

    def test_entry_update_view_post(self):
        """Test that an entry can be updated."""
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

    def test_entry_delete_view_get(self):
        """Test that the entry delete view returns a 200 status code."""
        response = self.client.get(self.delete_url)
        assert response.status_code == 200

    def test_entry_delete_view_post(self):
        """Test that an entry can be deleted."""
        entry_count = DiaryEntry.objects.count()
        response = self.client.post(self.delete_url)
        assert response.status_code == 302  # Redirect after successful deletion
        assert DiaryEntry.objects.count() == entry_count - 1
        assert not DiaryEntry.objects.filter(pk=self.entry.pk).exists()
