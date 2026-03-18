---
name: test-gen
description: This skill should be used when the user asks to generate tests, write unit tests, create test cases, add test coverage, write integration tests, or create a test suite for their code. Trigger phrases include "generate tests", "write unit tests", "add test coverage", "create test cases", "write tests for this", "generate a test suite", "add tests".
version: 1.0.0
license: MIT
allowed-tools:
  - read
  - write
  - bash
metadata:
  version: "1.0"
  tags: [testing, unit-tests, pytest, jest, coverage]
---

# test-gen — Intelligent Test Generator

Read source files and automatically generate comprehensive test suites — unit tests, edge cases, and error paths. Supports Python (pytest) and JavaScript/TypeScript (Jest/Vitest).

## How to use

```
/test-gen [file or directory]
```

## Instructions

### Step 1 — Read the source file

Read `$ARGUMENTS` and detect the language.

### Step 2 — Analyze what to test

Identify:
- All public functions/methods/classes
- Parameters and their types/constraints
- Return values and possible error states
- Dependencies that need mocking

### Step 3 — Generate the test file

**Python:** Use `templates/pytest_template.py` as the base structure.
**JS/TS:** Use `templates/jest_template.js` as the base structure.

Run the scaffolding script to create the file skeleton:

```bash
python3 ${SKILL_DIR}/scripts/scaffold_tests.py "$ARGUMENTS"
```

Then fill in the actual test logic based on the source.

### Step 4 — Validate tests run

```bash
# Python
python3 -m pytest <test_file> -v 2>&1 | head -50

# JS/TS
npx jest <test_file> --no-coverage 2>&1 | head -50
```

### Coverage targets

- Happy path: 100%
- Error/exception paths: 100%
- Edge cases (null, empty, boundary): minimum 3 per function
- Integration points: mock all external deps
