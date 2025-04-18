import pytest
from playwright.sync_api import Page, expect
from asgiref.sync import sync_to_async
from ui_tests.conftest import TEST_USER

# Base URL for the application
BASE_URL = "http://127.0.0.1:8000"

@pytest.fixture(scope="function", autouse=True)
async def setup_test_user(django_db_setup, django_db_blocker):
    """Create a test user for UI tests."""
    from django.contrib.auth.models import User

    # Define async functions to handle database operations
    @sync_to_async
    def create_test_user():
        with django_db_blocker.unblock():
            # Get or create the test user
            user, created = User.objects.get_or_create(
                username=TEST_USER["username"],
                defaults={
                    "email": TEST_USER["email"],
                }
            )

            # Set password (needed even if user already exists)
            user.set_password(TEST_USER["password"])
            user.save()
            return user

    @sync_to_async
    def create_test_entry(user):
        from code_diary.models import DiaryEntry
        from django.utils import timezone

        with django_db_blocker.unblock():
            # Check if the user already has entries
            if not DiaryEntry.objects.filter(user=user, title="Test Entry").exists():
                DiaryEntry.objects.create(
                    user=user,
                    date=timezone.now().date(),
                    title="Test Entry",
                    content="This is a test entry created for UI testing.",
                    technologies="Python, Django, Playwright"
                )

    # Create the test user and entry
    user = await create_test_user()
    await create_test_entry(user)

    yield user

    # We don't delete the user after tests to avoid issues with parallel test runs
    # The cleanup_test_data fixture in conftest.py handles this for us

def test_home_page_loads(page: Page):
    """Test that the home page loads correctly."""
    # Navigate to the home page
    page.goto(BASE_URL)

    # Check that the page title is correct
    expect(page).to_have_title("Home - Code Diary")

    # Check that the main heading is present
    heading = page.locator("h1")
    expect(heading).to_contain_text("Welcome to Code Diary")

    # Check that the navigation bar is present
    nav = page.locator(".navbar")
    expect(nav).to_be_visible()

def test_login_functionality(page: Page):
    """Test the login functionality."""
    # Navigate to the login page
    page.goto(f"{BASE_URL}/diary/login/")

    # Check that the login form is present
    expect(page.locator("form")).to_be_visible()

    # Fill in the login form
    page.fill("input[name='username']", TEST_USER["username"])
    page.fill("input[name='password']", TEST_USER["password"])

    # Submit the form
    page.click("button[type='submit']")

    # Check that we're redirected to the my entries page
    expect(page).to_have_url(f"{BASE_URL}/diary/my-entries/")

    # Check that the user is logged in (username is visible in the navbar)
    user_dropdown = page.locator(".dropdown-toggle:has-text('" + TEST_USER["username"] + "')")
    expect(user_dropdown).to_be_visible()

def test_view_diary_entries(page: Page):
    """Test viewing diary entries."""
    # Login first
    page.goto(f"{BASE_URL}/diary/login/")
    page.fill("input[name='username']", TEST_USER["username"])
    page.fill("input[name='password']", TEST_USER["password"])
    page.click("button[type='submit']")

    # Navigate to my entries page
    page.goto(f"{BASE_URL}/diary/my-entries/")

    # Check that the entries are displayed
    # Use first() to get only the first matching element and avoid strict mode violation
    entries = page.locator(".card-title").first
    expect(entries).to_contain_text("Test Entry")

    # Click on an entry to view details
    page.click("a:has-text('Test Entry')")

    # Check that we're on the entry detail page (checking URL pattern manually)
    current_url = page.url
    assert current_url.startswith(f"{BASE_URL}/diary/entry/") and current_url.endswith("/"), \
        f"Expected URL to start with {BASE_URL}/diary/entry/ and end with /, but got {current_url}"

    # Check that the entry content is displayed
    content = page.locator(".content")
    # Just check that there is some content, without checking the exact text
    expect(content).to_be_visible()

def test_create_diary_entry(page: Page):
    """Test creating a new diary entry."""
    # Login first
    page.goto(f"{BASE_URL}/diary/login/")
    page.fill("input[name='username']", TEST_USER["username"])
    page.fill("input[name='password']", TEST_USER["password"])
    page.click("button[type='submit']")

    # Navigate to the create entry page
    page.goto(f"{BASE_URL}/diary/entry/new/")

    # Check that the form is displayed
    expect(page.locator("form")).to_be_visible()

    # Fill in the form
    import datetime
    today = datetime.date.today().strftime("%Y-%m-%d")

    page.fill("input[name='date']", today)
    page.fill("input[name='title']", "New UI Test Entry")
    page.fill("textarea[name='content']", "This is a new entry created during UI testing.")
    page.fill("input[name='technologies']", "Python, Django, Playwright, Testing")

    # Submit the form
    page.click("button:has-text('Create Entry')")

    # Check that we're redirected to the my entries page
    expect(page).to_have_url(f"{BASE_URL}/diary/my-entries/")

    # Check that the new entry is displayed
    # Use first() to get only the first matching element and avoid strict mode violation
    new_entry = page.locator(".card-title:has-text('New UI Test Entry')").first
    expect(new_entry).to_be_visible()
