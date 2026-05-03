@echo off
REM Test Runner Script for Discord Multi-Agent System
REM This script helps run tests on Windows

echo ===================================================
echo   Discord Multi-Agent System - Test Runner
echo ===================================================
echo.

REM Check if Python is available
where python >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Python found in PATH
    python --version
) else (
    echo [INFO] Python not in PATH, trying common locations...
    
    REM Try WorkBuddy Python
    if exist "C:\Users\L\.workbuddy\binaries\python\versions\3.13.12\python.exe" (
        set PYTHON="C:\Users\L\.workbuddy\binaries\python\versions\3.13.12\python.exe"
        echo [OK] Found WorkBuddy Python
        goto :run_tests
    )
    
    REM Try system Python
    if exist "C:\Python311\python.exe" (
        set PYTHON="C:\Python311\python.exe"
        echo [OK] Found system Python
        goto :run_tests
    )
    
    echo [ERROR] Python not found! Please install Python or add it to PATH.
    pause
    exit /b 1
)

set PYTHON=python

:run_tests
echo.
echo [INFO] Running tests...
echo.

%PYTHON% -m pip install -q -r requirements.txt
%PYTHON% -m pip install -q -r requirements-dev.txt

echo.
echo ===================================================
echo   Running Unit Tests
echo ===================================================
%PYTHON% -m pytest tests/ -v --tb=short

echo.
echo ===================================================
echo   Running Tests with Coverage
echo ===================================================
%PYTHON% -m pytest tests/ --cov=src --cov-report=term-missing

echo.
echo ===================================================
echo   Test Run Complete!
echo ===================================================
pause
