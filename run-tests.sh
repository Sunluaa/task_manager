#!/bin/bash

echo "=== Task Management System - Test Suite ==="
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "Installing pytest..."
    pip install pytest pytest-asyncio httpx
fi

echo "Running Auth Service Tests..."
cd auth-service
pytest tests/test_auth.py -v --tb=short
AUTH_RESULT=$?
cd ..

echo ""
echo "Running Tasks Service Tests..."
cd tasks-service
pytest tests/test_tasks.py -v --tb=short
TASKS_RESULT=$?
cd ..

echo ""
echo "=== Test Summary ==="
if [ $AUTH_RESULT -eq 0 ]; then
    echo "✓ Auth Service Tests: PASSED"
else
    echo "✗ Auth Service Tests: FAILED"
fi

if [ $TASKS_RESULT -eq 0 ]; then
    echo "✓ Tasks Service Tests: PASSED"
else
    echo "✗ Tasks Service Tests: FAILED"
fi

# Total result
if [ $AUTH_RESULT -eq 0 ] && [ $TASKS_RESULT -eq 0 ]; then
    echo ""
    echo "All tests PASSED!"
    exit 0
else
    echo ""
    echo "Some tests FAILED!"
    exit 1
fi
