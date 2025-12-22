import sys
import os

def pytest_configure(config):
    """Configure pytest for tasks-service tests"""
    tasks_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    # Only add to path if not already there
    if tasks_path not in sys.path:
        sys.path.insert(0, tasks_path)
