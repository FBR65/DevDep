---
bootstrap: superpowers
version: 1.0.0
---

# Superpowers Bootstrap

## Session Initialization

This file is loaded at the start of every Superpowers session.
It establishes the development context and enforces the skill check protocol.

## 1. Load Core System

Read `.superpowers/skills/SKILL.md` to understand:
- The 1% Rule
- Development Pipeline
- Session Lifecycle
- Tool Mapping

## 2. Skill Discovery

Scan `.superpowers/skills/` for all `SKILL.md` files and sub-skills.
For each skill found:
- Read YAML frontmatter (between `---` delimiters)
- Note: skill slug, name, description, triggers
- Add to available skills registry

## 3. Context Loading

Read project context files:
- `devdep/workspace/SPEC.md` — Project specification
- `devdep/workspace/PLAN.md` — Current implementation plan
- `pyproject.toml` — Project configuration
- `requirements.txt` — Dependencies

## 4. State Assessment

Determine current session state:
- [ ] Fresh start — no PLAN.md exists
- [ ] Planning phase — PLAN.md exists but not approved
- [ ] Development phase — PLAN.md approved, tasks in progress
- [ ] Finishing phase — all tasks complete, ready for validation

## 5. Skill Invocation

Based on state, invoke appropriate skill:
- Fresh start → `brainstorming`
- Planning needed → `writing-plans`
- Implementation ready → `subagent-dev`
- Completion ready → `finishing`

## 6. Mandatory Checks

Before any action:
- [ ] 1% Rule scan completed
- [ ] SPEC.md read and understood
- [ ] Current state identified
- [ ] Appropriate skill selected

## Bootstrap Command

To initialize a Superpowers session, run:

```bash
uv run python -m devdep.superpowers bootstrap
```

Or from Python:

```python
from devdep.superpowers import SuperpowersSession
session = SuperpowersSession()
session.bootstrap()
```
