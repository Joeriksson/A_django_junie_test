import pytest
from playwright.sync_api import Page, expect
from asgiref.sync import sync_to_async
from ui_tests.conftest import TEST_USER

# Base URL for the application
BASE_URL = "http://127.0.0.1:8000"

@pytest.fixture(scope="function")
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

    # Print debug information about the user
    @sync_to_async
    def debug_user_info():
        from django.contrib.auth.models import User
        with django_db_blocker.unblock():
            # Check if the user exists
            user_exists = User.objects.filter(username=TEST_USER["username"]).exists()
            user_count = User.objects.filter(username=TEST_USER["username"]).count()
            print(f"Debug - User '{TEST_USER['username']}' exists: {user_exists}, count: {user_count}")

            if user_exists:
                # Get the user and check if the password is correct
                test_user = User.objects.get(username=TEST_USER["username"])
                password_valid = test_user.check_password(TEST_USER["password"])
                print(f"Debug - Password valid for user '{TEST_USER['username']}': {password_valid}")

                # Check if the user has entries
                from code_diary.models import DiaryEntry
                entry_count = DiaryEntry.objects.filter(user=test_user).count()
                print(f"Debug - User '{TEST_USER['username']}' has {entry_count} entries")

    await debug_user_info()
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

@pytest.mark.django_db
def test_entry_detail_view(page: Page):
    """Test viewing a diary entry detail page."""
    # Get the test user and create an entry
    from django.contrib.auth.models import User
    from code_diary.models import DiaryEntry
    import os

    # Set environment variable to allow async unsafe operations
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

    # Create a test user
    user, created = User.objects.get_or_create(
        username=TEST_USER["username"],
        defaults={
            "email": TEST_USER["email"],
        }
    )

    # Set password (needed even if user already exists)
    user.set_password(TEST_USER["password"])
    user.save()

    print(f"{'Created' if created else 'Using existing'} test user '{user.username}' with ID {user.id}")

    # Get an existing entry from the database
    entry = DiaryEntry.objects.first()
    if not entry:
        # If no entries exist, create one
        from django.utils import timezone
        entry = DiaryEntry.objects.create(
            user=user,
            date=timezone.now().date(),
            title="Test Entry for Detail View",
            content="This is a test entry created for UI testing the detail view.",
            technologies="Python, Django, Playwright"
        )

    # Print all entries in the database for debugging
    all_entries = DiaryEntry.objects.all()
    print(f"All entries in database: {[f'ID: {e.id}, Title: {e.title}, User: {e.user.username}' for e in all_entries]}")

    print(f"Using entry '{entry.title}' with ID {entry.id}")

    # Use reverse to get the correct URL
    from django.urls import reverse
    entry_url = reverse('code_diary:entry_detail', kwargs={'pk': entry.id})
    full_url = f"{BASE_URL}{entry_url}"
    print(f"Navigating to entry detail page at: {full_url}")

    # Navigate directly to the entry detail page
    page.goto(full_url)

    # Print the current URL for debugging
    print(f"Current URL: {page.url}")

    # Take a screenshot for debugging
    page.screenshot(path="entry_detail.png")

    # Wait for the page to load completely
    page.wait_for_load_state("networkidle")

    # Check that the entry title is displayed
    expect(page.locator("h1")).to_contain_text(entry.title)

    # Check that the entry content is displayed
    expect(page.locator(".content")).to_contain_text(entry.content)

    # Check that the entry technologies are displayed
    expect(page.locator(".technologies")).to_contain_text(entry.technologies)

    # Check that the entry date is displayed
    date_str = entry.date.strftime("%B %-d, %Y")  # Use %-d to remove leading zero
    # Use a more specific selector that targets only the paragraph containing the date
    expect(page.locator("p.text-muted")).to_contain_text(f"Date: {date_str}")

def test_view_diary_entries(page: Page):
    """Test viewing diary entries."""
    # Login first
    page.goto(f"{BASE_URL}/diary/login/")
    page.fill("input[name='username']", TEST_USER["username"])
    page.fill("input[name='password']", TEST_USER["password"])

    # Print the current state for debugging
    print(f"Attempting to log in with username: {TEST_USER['username']}")

    # Submit the form
    page.click("button[type='submit']")

    # Wait for either a redirect or for the page to stabilize
    page.wait_for_load_state("networkidle")

    # Check if we're still on the login page (which would indicate a failed login)
    current_url = page.url
    if "/login/" in current_url:
        # Check for error messages
        error_message = page.locator(".alert-danger").text_content() if page.locator(".alert-danger").count() > 0 else "No error message displayed"
        print(f"Login failed. Current URL: {current_url}, Error: {error_message}")

        # Take a screenshot for debugging
        page.screenshot(path="view_entries_login_failure.png")

        # This will fail the test with a helpful message
        assert "/login/" not in current_url, f"Login failed. Current URL: {current_url}, Error: {error_message}"

    # If we got here, we should be on the my entries page
    print(f"Login successful. Current URL: {current_url}")

    # Navigate to my entries page
    page.goto(f"{BASE_URL}/diary/my-entries/")

    # Wait for the page to load completely
    page.wait_for_load_state("networkidle")

    # Wait for the entries to be visible
    page.wait_for_selector(".card", timeout=5000)

    # Check that the entries are displayed
    # Use a more specific selector to find the entry title
    entries = page.locator(".card-title:has-text('Test Entry')")
    expect(entries).to_be_visible()

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

    # Print the current state for debugging
    print(f"Attempting to log in with username: {TEST_USER['username']}")

    # Submit the form
    page.click("button[type='submit']")

    # Wait for either a redirect or for the page to stabilize
    page.wait_for_load_state("networkidle")

    # Check if we're still on the login page (which would indicate a failed login)
    current_url = page.url
    if "/login/" in current_url:
        # Check for error messages
        error_message = page.locator(".alert-danger").text_content() if page.locator(".alert-danger").count() > 0 else "No error message displayed"
        print(f"Login failed. Current URL: {current_url}, Error: {error_message}")

        # Take a screenshot for debugging
        page.screenshot(path="create_entry_login_failure.png")

        # This will fail the test with a helpful message
        assert "/login/" not in current_url, f"Login failed. Current URL: {current_url}, Error: {error_message}"

    # If we got here, we should be on the my entries page
    print(f"Login successful. Current URL: {current_url}")

    # Navigate to the create entry page
    page.goto(f"{BASE_URL}/diary/entry/new/")

    # Wait for the page to load completely
    page.wait_for_load_state("networkidle")

    # Wait for the form to be visible
    page.wait_for_selector("form", timeout=5000)

    # Check that the form is displayed
    expect(page.locator("form")).to_be_visible()

    # Wait for the date field to be visible
    page.wait_for_selector("input[type='date']", timeout=5000)

    # Fill in the form
    import datetime
    today = datetime.date.today().strftime("%Y-%m-%d")

    # Use a more specific selector for the date field
    page.fill("input[type='date']", today)
    page.fill("input[name='title']", "New UI Test Entry")
    page.fill("textarea[name='content']", "This is a new entry created during UI testing.")
    page.fill("input[name='technologies']", "Python, Django, Playwright, Testing")

    # Submit the form
    page.click("button:has-text('Create Entry')")

    # Wait for navigation to complete
    page.wait_for_url(f"{BASE_URL}/diary/my-entries/", timeout=10000)

    # Check that we're redirected to the my entries page
    expect(page).to_have_url(f"{BASE_URL}/diary/my-entries/")

    # Wait for the page to load completely
    page.wait_for_load_state("networkidle")

    # Wait for the entries to be visible
    page.wait_for_selector(".card", timeout=5000)

    # Check that the new entry is displayed
    new_entry = page.locator(".card-title:has-text('New UI Test Entry')")
    expect(new_entry).to_be_visible()
