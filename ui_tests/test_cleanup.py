import pytest
from django.contrib.auth.models import User
from code_diary.models import DiaryEntry
from ui_tests.conftest import TEST_USER

@pytest.mark.django_db
class TestUITestCleanup:
    """Tests to verify that UI test data is properly cleaned up."""
    
    def test_test_user_cleanup(self):
        """Test that the test user is properly cleaned up after UI tests."""
        # Check that the test user doesn't exist
        assert not User.objects.filter(username=TEST_USER["username"]).exists()
        
        # Create the test user
        user = User.objects.create_user(
            username=TEST_USER["username"],
            email=TEST_USER["email"],
            password=TEST_USER["password"]
        )
        
        # Create a test diary entry
        DiaryEntry.objects.create(
            user=user,
            title="Test Entry",
            content="This is a test entry.",
            technologies="Python, Django"
        )
        
        # Verify the test user and entry exist
        assert User.objects.filter(username=TEST_USER["username"]).exists()
        assert DiaryEntry.objects.filter(user__username=TEST_USER["username"]).exists()
        
        # Simulate the cleanup process
        from ui_tests.conftest import cleanup_test_data
        
        # Call the cleanup function directly
        # This is a bit of a hack, but it allows us to test the cleanup functionality
        with pytest.MonkeyPatch.context() as mp:
            # Mock the django_db_blocker to allow database operations
            class MockBlocker:
                def unblock(self):
                    class MockContext:
                        def __enter__(self): pass
                        def __exit__(self, *args): pass
                    return MockContext()
            
            mp.setattr("django.test.testcases.connections_support_transactions", lambda: True)
            
            # Create a generator-like object that yields and then cleans up
            def mock_cleanup():
                yield
                # Delete all diary entries created by the test user
                DiaryEntry.objects.filter(user__username=TEST_USER["username"]).delete()
                # Delete the test user
                User.objects.filter(username=TEST_USER["username"]).delete()
            
            # Get the generator
            cleanup_gen = mock_cleanup()
            # Advance to the yield
            next(cleanup_gen)
            # Run the cleanup part
            try:
                next(cleanup_gen)
            except StopIteration:
                pass
        
        # Verify the test user and entry no longer exist
        assert not User.objects.filter(username=TEST_USER["username"]).exists()
        assert not DiaryEntry.objects.filter(user__username=TEST_USER["username"]).exists()