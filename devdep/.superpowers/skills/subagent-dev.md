---
skill: subagent-dev
name: Subagent-Driven Development
description: |
  Delegate implementation tasks to subagents following the plan.
  Each subagent gets one task, executes TDD, and reports back.
triggers:
  - Plan is approved and ready for implementation
  - Task is complex enough to delegate
  - Parallel development is possible
---

# Subagent-Driven Development Skill

## Purpose

Break approved plans into discrete tasks and delegate each to a subagent.
Each subagent operates independently with clear scope and acceptance criteria.

## Workflow

1. **Load Approved Plan**
   - Read PLAN.md
   - Identify tasks ready for implementation
   - Verify dependencies are met

2. **Create Subagent Tasks**
   - One subagent per task
   - Each subagent receives:
     - Task description
     - Acceptance criteria
     - Relevant files to read
     - TDD requirements

3. **Delegate and Monitor**
   - Spawn subagent with `new_task` tool
   - Provide clear instructions
   - Wait for completion report

4. **Review and Integrate**
   - Review subagent output against acceptance criteria
   - Run tests to verify
   - Integrate changes into main branch

## Subagent Instructions Template

```
You are implementing Task [N]: [Task Name]

## Context
Read these files first:
- devdep/workspace/SPEC.md
- devdep/workspace/PLAN.md
- [relevant source files]

## Task
[Detailed description of what to implement]

## TDD Requirements
1. Write a failing test first (RED)
2. Implement minimal code to pass (GREEN)
3. Refactor while keeping tests green

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Constraints
- Do not modify files outside your scope
- Follow existing code style
- All tests must pass before completion
```

## Integration Rules

- Subagents must not modify PLAN.md or SPEC.md
- Subagents must report which files they changed
- Main agent verifies all tests pass before accepting
- Failed subagent tasks are retried with clearer instructions
