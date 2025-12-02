# Test Suite Examples

This document provides concrete examples of what each type of test validates in the README.md file.

## Example Test Scenarios

### ✅ Tests That PASS (Current README.md)

#### 1. File Structure Tests
```javascript
// ✅ PASSES: File exists
test('README.md file should exist')
// Current: README.md exists at repository root

// ✅ PASSES: Has content
test('README.md should not be empty')
// Current: File has 4 lines of content
```

#### 2. Heading Tests
```javascript
// ✅ PASSES: Has primary heading
test('should have a primary heading (h1)')
// Current: "# course-sdlc" ← Valid h1

// ✅ PASSES: Proper formatting
test('should have well-formed markdown headings')
// Current: "# course-sdlc" ← Space after # ✓
```

#### 3. Content Tests
```javascript
// ✅ PASSES: Contains project description
test('should contain project description')
// Current: "Course of SDLC using AI" ← Present ✓

// ✅ PASSES: Recent changes present
test('should contain the recent change about qodo')
// Current: "Change for test qodo" ← Present ✓
```

#### 4. Security Tests
```javascript
// ✅ PASSES: No exposed secrets
test('should not contain potential security issues')
// Current: No API keys, passwords, or secrets detected ✓

// ✅ PASSES: No PII
test('should not contain personally identifiable information')
// Current: No email addresses or personal info detected ✓
```

### ❌ Tests That Would FAIL (If README.md had issues)

#### 1. Missing Content
```javascript
// ❌ WOULD FAIL if content removed
test('should mention AI in the description')
// Would fail if: "Course of SDLC" (missing "using AI")
```

#### 2. Malformed Markdown
```javascript
// ❌ WOULD FAIL with bad formatting
test('should have well-formed markdown headings')
// Would fail if: "#course-sdlc" (no space after #)
// Would fail if: "# course-sdlc #" (trailing #)
```

#### 3. Security Issues
```javascript
// ❌ WOULD FAIL with exposed secrets
test('should not contain potential security issues')
// Would fail if: "api_key = '12345abcde'"
// Would fail if: "password = 'secret123'"
```

#### 4. Formatting Problems
```javascript
// ❌ WOULD FAIL with trailing whitespace
test('should not have trailing whitespace on lines')
// Would fail if: "# course-sdlc    " (spaces at end)

// ❌ WOULD FAIL without newline
test('should end with a newline character (POSIX standard)')
// Would fail if file doesn't end with \n
```

## Real-World Test Execution Examples

### Example 1: All Tests Pass

```bash
$ npm test

PASS  tests/readme.test.js (2.345s)
  README.md Validation Tests
    File Existence and Basic Structure
      ✓ README.md file should exist (5ms)
      ✓ README.md should not be empty (2ms)
      ✓ README.md should contain actual content beyond whitespace (1ms)
    Title and Heading Structure
      ✓ should have a primary heading (h1) (3ms)
      ✓ primary heading should be "course-sdlc" (2ms)
      ✓ should have well-formed markdown headings (1ms)
      ✓ should not have trailing hashes in ATX-style headings (1ms)
    Content Quality and Completeness
      ✓ should contain project description (2ms)
      ✓ should mention AI in the description (1ms)
      ✓ should have substantive content (more than just title) (1ms)
      ✓ should contain the recent change about qodo (2ms)
    [... 54 more tests ...]

PASS  tests/readme.lint.test.js (1.234s)
PASS  tests/readme.changes.test.js (0.987s)

Test Suites: 3 passed, 3 total
Tests:       65 passed, 65 total
Snapshots:   0 total
Time:        4.566s
Ran all test suites.
```

### Example 2: Test Failure with Details

```bash
$ npm test

FAIL  tests/readme.test.js
  README.md Validation Tests
    Content Quality and Completeness
      ✕ should mention AI in the description (12ms)

  ● README.md Validation Tests › Content Quality and Completeness › should mention AI in the description

    expect(received).toContain(expected)

    Expected substring: "ai"
    Received string: "# course-sdlc\nCourse of SDLC\n\nChange for test qodo"

      59 |     test('should mention AI in the description', () => {
      60 |       expect(readmeContent.toLowerCase()).toContain('ai');
    > 61 |     });
         |       ^

      at Object.<anonymous> (tests/readme.test.js:61:7)

Test Suites: 1 failed, 2 passed, 3 total
Tests:       1 failed, 64 passed, 65 total
```

### Example 3: Running Specific Tests

```bash
# Run only security tests
$ npm test -- --testNamePattern="security|PII"

PASS  tests/readme.test.js
  README.md Validation Tests
    File Integrity and Security
      ✓ should not contain potential security issues (8ms)
      ✓ should not contain personally identifiable information (5ms)

Tests:       2 passed, 2 total
```

## What Each Test File Tests

### readme.test.js (Core Validation)

**Tests your README for:**
- Does the file exist? ✓
- Is it properly formatted markdown? ✓
- Are headings structured correctly? ✓
- Is the content complete and meaningful? ✓
- Are links formatted properly? ✓
- Are there any security issues? ✓
- Is it accessible and following best practices? ✓
- Does it handle edge cases gracefully? ✓

### readme.lint.test.js (Markdown Linting)

**Tests for markdown quality:**
- Are URLs properly wrapped in links? ✓
- Is emphasis (bold/italic) consistent? ✓
- Are lists properly formatted? ✓
- Are code blocks language-tagged? ✓
- Are there common markdown mistakes? ✓
- Is the documentation complete? ✓

### readme.changes.test.js (Change Validation)

**Tests the recent changes:**
- Is the new "qodo test" content present? ✓
- Were any critical parts removed? ✓
- Is the change grammatically correct? ✓
- Does it maintain professional tone? ✓
- Is the file still valid after changes? ✓
- Can more content be added easily? ✓

## Practical Testing Workflow

### Scenario 1: Adding New Content to README

```bash
# 1. Make changes to README.md
echo "\n## Installation\nnpm install" >> README.md

# 2. Run tests to verify
npm test

# 3. If tests fail, fix the issues
# Example: Test fails because no newline at end
echo "" >> README.md

# 4. Verify tests pass
npm test

# 5. Commit changes
git add README.md
git commit -m "Add installation section"
```

### Scenario 2: Checking for Security Issues

```bash
# Run only security-related tests
npm test -- --testNamePattern="security|PII|secrets"

# If you accidentally added sensitive info:
# FAIL: should not contain potential security issues
# Fix by removing the sensitive data, then retest
```

### Scenario 3: Pre-commit Hook

```bash
# Add to .git/hooks/pre-commit
#!/bin/bash
npm test
if [ $? -ne 0 ]; then
  echo "Tests failed! Commit aborted."
  exit 1
fi
```

## Coverage Examples

### Running Coverage Report

```bash
$ npm run test:coverage

PASS  tests/readme.test.js
PASS  tests/readme.lint.test.js
PASS  tests/readme.changes.test.js

----------------------|---------|----------|---------|---------|
File                  | % Stmts | % Branch | % Funcs | % Lines |
----------------------|---------|----------|---------|---------|
All files             |     100 |      100 |     100 |     100 |
 README.md validation |     100 |      100 |     100 |     100 |
----------------------|---------|----------|---------|---------|

Test Suites: 3 passed, 3 total
Tests:       65 passed, 65 total
Time:        4.566s
```

## Common Issues and Solutions

### Issue 1: Tests fail after editing README

**Problem:**