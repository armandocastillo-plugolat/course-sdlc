# README.md Test Suite

This directory contains comprehensive tests for validating the README.md file of the course-sdlc project.

## Test Structure

### 1. `readme.test.js` - Core Validation Tests (36 tests)
Comprehensive unit tests covering:
- File Existence and Basic Structure
- Title and Heading Structure
- Content Quality and Completeness
- Markdown Syntax Validation
- Link Validation
- Formatting and Style Consistency
- Content Specificity Tests
- File Integrity and Security
- Accessibility and Best Practices
- Edge Cases and Error Handling
- Version Control and Metadata

### 2. `readme.lint.test.js` - Markdown Linting Integration Tests (13 tests)
Advanced markdown linting tests:
- Markdown Best Practices
- Common Markdown Mistakes
- GitHub Flavored Markdown Features
- Documentation Completeness

### 3. `readme.changes.test.js` - Change-Specific Validation (16 tests)
Tests specifically for the recent changes:
- Change Quality
- Git Diff Analysis
- Content Evolution
- Change Integration
- Future Extensibility

## Running Tests

### Install Dependencies
```bash
npm install
```

### Run All Tests
```bash
npm test
```

### Run Tests in Watch Mode
```bash
npm run test:watch
```

### Generate Coverage Report
```bash
npm run test:coverage
```

### Run Specific Test Suite
```bash
npm test -- tests/readme.test.js
npm test -- tests/readme.lint.test.js
npm test -- tests/readme.changes.test.js
```

## Test Coverage

Total: **65 comprehensive tests** across 23 test suites covering:
- ✅ File structure and syntax
- ✅ Content quality and completeness
- ✅ Markdown best practices
- ✅ Link integrity
- ✅ Security and PII checks
- ✅ Accessibility compliance
- ✅ Change quality validation
- ✅ Git integration
- ✅ Future extensibility

## Quick Start

```bash
# Install dependencies
npm install

# Run tests
npm test
```

Expected output: All 65 tests should pass ✓