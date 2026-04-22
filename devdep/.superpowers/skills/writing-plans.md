---
skill: writing-plans
name: Writing Implementation Plans
description: |
  Create structured, testable implementation plans that align with SPEC.md.
  Must be invoked before any implementation. Enforces HARD-GATE approval.
triggers:
  - After brainstorming completes
  - Before any code implementation
  - When SPEC.md changes
  - When a plan needs updating
---

# Writing Plans Skill

## Purpose

Create a detailed, step-by-step implementation plan that:
- Aligns with SPEC.md requirements
- Defines testable acceptance criteria
- Estimates effort for each step
- Identifies dependencies and risks

## Workflow

1. **Read SPEC.md**
   - Extract all functional requirements
   - Extract all non-functional requirements
   - Note constraints and assumptions

2. **Define Tasks**
   - Break implementation into small, testable tasks
   - Each task should be completable in < 30 minutes
   - Order tasks by dependency (what must come first)

3. **Write TDD Steps**
   - For each task, define the test-first approach:
     - What test will be written first?
     - What is the expected failure?
     - What is the minimal implementation?
     - What confirms the test passes?

4. **Define Acceptance Criteria**
   - Each task must have clear "done" criteria
   - Criteria must be verifiable (test, check, or review)

5. **Output PLAN.md**
   - Write to `devdep/workspace/PLAN.md` or relevant location
   - Include task list with checkboxes
   - Include dependency graph
   - Include risk assessment

## HARD-GATE: Plan Approval

Before ANY implementation:
- [ ] Plan reviewed against SPEC.md
- [ ] All tasks have acceptance criteria
- [ ] TDD steps defined for each task
- [ ] Dependencies identified and ordered
- [ ] **APPROVED** — proceed to subagent-driven-development

## Plan Template

```markdown
# Implementation Plan: [Feature Name]

## Overview
Brief description of what this plan implements.

## Dependencies
- Files that must exist before starting
- Skills that must be invoked
- External services or data needed

## Tasks

### Task 1: [Name]
**Goal:** What this task achieves
**Files:** Which files are created/modified
**TDD Steps:**
- [ ] RED: Write failing test for [specific behavior]
- [ ] GREEN: Implement minimal [function/class]
- [ ] REFACTOR: Clean up while tests pass
**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2

### Task 2: [Name]
...

## Risk Assessment
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| ... | ... | ... | ... |
```
