import pytest
import time
import os

# Tests to demonstrate parallel execution
@pytest.mark.parametrize("test_id", range(5))
def test_parallel_execution(test_id):
    """Test that demonstrates parallel execution."""
    # Get the worker ID to show which worker is running the test
    worker_id = os.environ.get("PYTEST_XDIST_WORKER", "main")
    
    # Sleep for a short time to simulate work
    time.sleep(0.5)
    
    # Print a message to show which worker is running the test
    print(f"Test {test_id} running on worker {worker_id}")
    
    # Assert something trivial
    assert True