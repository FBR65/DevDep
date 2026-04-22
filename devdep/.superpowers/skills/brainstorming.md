---
skill: brainstorming
name: Brainstorming and Exploration
description: |
  Generate ideas, explore approaches, and evaluate options before committing to a plan.
  Must be invoked when starting any new feature, refactoring, or architectural decision.
triggers:
  - New feature request
  - Architectural decision needed
  - Multiple implementation options exist
  - Unclear how to approach a problem
---

# Brainstorming Skill

## Purpose

Explore all viable approaches to a problem BEFORE writing any plan or code.
This skill prevents premature optimization and ensures the best approach is chosen.

## Workflow

1. **Understand the Problem**
   - Read SPEC.md if it exists
   - Read existing code related to the problem
   - Identify constraints and requirements

2. **Generate Options**
   - List at least 3 different approaches
   - For each approach, note pros and cons
   - Consider trade-offs: complexity, performance, maintainability

3. **Evaluate and Select**
   - Score each approach against requirements
   - Select the best approach with justification
   - Document why other approaches were rejected

4. **Output**
   - Write findings to a temporary `.superpowers/brainstorm/` file
   - Summarize the chosen approach in 2-3 sentences
   - Proceed to `writing-plans` skill

## Constraints

- NO code is written during brainstorming
- NO implementation details are decided
- Focus on WHAT and WHY, not HOW
- Timebox: maximum 10 minutes of exploration

## Example Output

```markdown
# Brainstorm: User Authentication

## Options Considered
1. **Session-based auth** — Pros: Simple. Cons: Doesn't scale, stateful.
2. **JWT in cookies** — Pros: Stateless, secure. Cons: XSS risk.
3. **JWT in Authorization header** — Pros: Stateless, API-friendly. Cons: Token management.

## Selected Approach
Option 3: JWT in Authorization header with refresh token rotation.
Best fit for REST API, aligns with SPEC.md requirements.

## Rejected
- Session-based: violates statelessness requirement
- Cookies: adds complexity for API clients
```
