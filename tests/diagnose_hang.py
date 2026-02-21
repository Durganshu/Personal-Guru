import pytest
import threading
import sys
import os

def run_tests():
    print("Running tests...")
    # Run specific tests that were hanging
    ret = pytest.main(["tests/test_app.py", "-k", "test_log_telemetry or test_dcs", "-vv"])
    print(f"Pytest finished with code: {ret}")

    print("\nActive Threads:")
    for thread in threading.enumerate():
        print(f"  {thread.name} (daemon={thread.daemon})")

    # Check if LogCapture thread is running
    # We can try to stop it manually if we find it

if __name__ == "__main__":
    # Force enable telemetry to reproduce issue if it's related to that, or disable to see if it fixes
    # We'll try to mirror the 'TestConfig' environment
    os.environ['Testing'] = 'True'
    run_tests()
