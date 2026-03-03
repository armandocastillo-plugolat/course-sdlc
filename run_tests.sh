#!/bin/bash
# Test runner script for course-sdlc

set -e

echo "========================================="
echo "Running Test Suite for course-sdlc"
echo "========================================="
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "pytest not found. Installing test dependencies..."
    pip install -r requirements-test.txt
fi

echo "Running unit tests..."
pytest tests/test_app.py -v

echo ""
echo "Running security tests..."
pytest tests/test_security.py -v

echo ""
echo "Running all tests with coverage..."
pytest --cov=src --cov-report=term-missing --cov-report=html

echo ""
echo "========================================="
echo "Test Summary"
echo "========================================="
pytest --co -q

echo ""
echo "Coverage report generated in htmlcov/index.html"
echo ""
echo "Done!"