import pytest
from playwright.sync_api import sync_playwright
import os

# Set environment variable to allow async unsafe operations
# This is a temporary solution for testing purposes
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

# Test data
TEST_USER = {
    "username": "testuser",
    "password": "testpassword",
    "email": "test@example.com"
}

# Configure Playwright for UI tests
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context for UI tests."""
    return {
        **browser_context_args,
        "viewport": {
            "width": 1280,
            "height": 720,
        },
        "ignore_https_errors": True,
        "java_script_enabled": True,
    }

# Add Django DB setup for UI tests
@pytest.fixture(scope="session")
def django_db_setup():
    """Configure Django DB for UI tests."""
    # Use the existing database configuration from settings
    # This avoids issues with missing settings like TIME_ZONE
    pass

# Cleanup fixture to remove test data after all tests are done
@pytest.fixture(scope="session", autouse=True)
async def cleanup_test_data(django_db_setup, django_db_blocker):
    """Clean up test data after all tests are done."""
    # This fixture runs before any tests
    yield

    # This part runs after all tests are done
    from asgiref.sync import sync_to_async
    from django.contrib.auth.models import User
    from code_diary.models import DiaryEntry

    @sync_to_async
    def cleanup_database():
        with django_db_blocker.unblock():
            # Delete all diary entries created by the test user
            DiaryEntry.objects.filter(user__username=TEST_USER["username"]).delete()

            # Delete the test user
            User.objects.filter(username=TEST_USER["username"]).delete()

            print(f"Cleaned up test user '{TEST_USER['username']}' and all associated diary entries.")

    await cleanup_database()
