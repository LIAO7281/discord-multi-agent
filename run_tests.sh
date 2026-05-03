#!/bin/bash
# Test Runner Script for Discord Multi-Agent System
# This script helps run tests on macOS/Linux

echo "==================================================="
echo "   Discord Multi-Agent System - Test Runner"
echo "==================================================="
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "[ERROR] Python not found! Please install Python 3.10+"
        exit 1
    else
        PYTHON=python
    fi
else
    PYTHON=python3
fi

echo "[OK] Using: $($PYTHON --version)"

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "[INFO] Creating virtual environment..."
    $PYTHON -m venv venv
fi

# Activate virtual environment
echo "[INFO] Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "[INFO] Installing dependencies..."
pip install -q -r requirements.txt
pip install -q -r requirements-dev.txt

echo ""
echo "==================================================="
echo "   Running Unit Tests"
echo "==================================================="
python -m pytest tests/ -v --tb=short

echo ""
echo "==================================================="
echo "   Running Tests with Coverage"
echo "==================================================="
python -m pytest tests/ --cov=src --cov-report=term-missing --cov-report=html

echo ""
echo "==================================================="
echo "   Code Quality Checks"
echo "==================================================="
echo "[INFO] Running flake8..."
flake8 src/ tests/ --max-line-length=127 --statistics || true

echo ""
echo "[INFO] Running black check..."
black --check src/ tests/ examples/ || true

echo ""
echo "==================================================="
echo "   Test Run Complete!"
echo "==================================================="
echo ""
echo "Coverage report: htmlcov/index.html"
