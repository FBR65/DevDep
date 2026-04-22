---
skill: finishing
name: Finishing a Development Branch
description: |
  Complete a development branch by running final tests, updating docs, and merging.
  Ensures quality gates are passed before completion.
triggers:
  - All plan tasks are complete
  - Ready to merge branch
  - Final validation needed
---

# Finishing Skill

## Purpose

Ensure all quality gates pass before marking a development branch as complete.

## Workflow

1. **Run Full Test Suite**
   - `pytest` — all tests must pass
   - Coverage check — minimum 80%
   - Lint check — no errors

2. **Verify Against SPEC.md**
   - All requirements implemented?
   - All endpoints working?
   - All schemas correct?

3. **Update Documentation**
   - Update README.md if needed
   - Update PLAN.md — mark all tasks complete
   - Add CHANGELOG entry

4. **Final Review**
   - Review all changed files
   - Check for debug code, TODOs, or hacks
   - Verify no secrets in code

5. **Merge and Cleanup**
   - Commit: `git add . && git commit -m "feat: Complete [feature name]"`
   - Merge to main branch
   - Delete feature branch

## Quality Gates

| Gate | Check | Pass Criteria |
|------|-------|---------------|
| Tests | `pytest` | 100% pass rate |
| Coverage | `pytest --cov` | ≥ 80% |
| Lint | `ruff check .` | 0 errors |
| Type Check | `mypy` | 0 errors |
| Security | Manual review | No secrets, safe defaults |

## Completion Criteria

- [ ] All tests pass
- [ ] SPEC.md requirements met
- [ ] Documentation updated
- [ ] Code reviewed
- [ ] Branch merged
