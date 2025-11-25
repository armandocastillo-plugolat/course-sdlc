# Quick Testing Guide

## 🚀 Getting Started

### 1. Install Test Dependencies
```bash
pip install -r requirements-test.txt
```

### 2. Run All Tests
```bash
pytest
```

### 3. Run Tests with Coverage
```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html  # View coverage report
```

### 4. Use the Test Runner Script
```bash
./run_tests.sh
```

## 📋 Test Suite Structure