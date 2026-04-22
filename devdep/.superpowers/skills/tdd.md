---
skill: tdd
name: Test-Driven Development
description: |
  Enforce RED-GREEN-REFACTOR cycle for all code changes.
  Must be invoked for any implementation task. No exceptions.
triggers:
  - Any code implementation
  - Bug fixes
  - Refactoring
  - Feature additions
---

# TDD Skill

## The RED-GREEN-REFACTOR Cycle

Every code change MUST follow this cycle exactly.

### 1. RED — Write a Failing Test

- Write a test that defines the desired behavior
- Run the test — it MUST fail
- If it passes, the test is wrong (or behavior already exists)
- Commit the failing test: `git add . && git commit -m "test: Add failing test for [feature]"`

### 2. GREEN — Make It Pass

- Write the MINIMAL code to make the test pass
- No refactoring yet
- No premature optimization
- Run the test — it MUST pass
- Commit: `git add . && git commit -m "feat: Implement [feature] to pass test"`

### 3. REFACTOR — Clean Up

- Improve code quality while keeping tests green
- Run tests after each change
- Commit: `git add . && git commit -m "refactor: Clean up [feature] implementation"`

## Test Requirements

- Tests must be in `tests/` directory
- Test files named `test_*.py`
- One test class per module being tested
- Tests must be independent (no shared state)
- Use pytest as the test runner

## Test Categories

1. **Unit Tests**: Test individual functions/classes in isolation
2. **Integration Tests**: Test component interactions
3. **API Tests**: Test endpoints with TestClient

## Example TDD Session

```python
# test_math.py — RED phase
# def test_add():
#     assert add(2, 3) == 5

# math.py — GREEN phase
def add(a, b):
    return a + b

# test_math.py — verify GREEN
# def test_add():
#     assert add(2, 3) == 5
#     assert add(-1, 1) == 0
```

## Forbidden

- Writing implementation before test
- Skipping the RED phase
- Committing without running tests
- Refactoring while tests are red
