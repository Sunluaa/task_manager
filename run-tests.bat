@echo off
REM Task Management System - Test Suite (Windows)

echo === Task Management System - Test Suite ===
echo.

REM Check if pytest is installed
pip show pytest >nul 2>&1
if errorlevel 1 (
    echo Installing pytest...
    pip install pytest pytest-asyncio httpx
)

echo Running Auth Service Tests...
cd auth-service
pytest tests/test_auth.py -v --tb=short
set AUTH_RESULT=%ERRORLEVEL%
cd ..

echo.
echo Running Tasks Service Tests...
cd tasks-service
pytest tests/test_tasks.py -v --tb=short
set TASKS_RESULT=%ERRORLEVEL%
cd ..

echo.
echo === Test Summary ===
if %AUTH_RESULT% equ 0 (
    echo ✓ Auth Service Tests: PASSED
) else (
    echo ✗ Auth Service Tests: FAILED
)

if %TASKS_RESULT% equ 0 (
    echo ✓ Tasks Service Tests: PASSED
) else (
    echo ✗ Tasks Service Tests: FAILED
)

if %AUTH_RESULT% equ 0 if %TASKS_RESULT% equ 0 (
    echo.
    echo All tests PASSED!
    exit /b 0
) else (
    echo.
    echo Some tests FAILED!
    exit /b 1
)
