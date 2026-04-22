---
skill: superpowers-core
name: superpowers-core-system
version: 1.0.0
description: |
  The core skill that governs all Superpowers development workflows.
  Enforces the 1% Rule, mandatory skill checks, TDD, and structured planning.
platforms: [claude-code, cursor, opencode, codex, gemini-cli, copilot-cli]
---

# Superpowers Core System

## The 1% Rule (Mandatory)

> **If there is even a 1% chance that a skill applies to the current task, you MUST invoke it.**

Before any implementation, planning, or decision:
1. Scan the `.superpowers/skills/` directory for all `SKILL.md` files
2. Read each skill's YAML frontmatter (between `---` delimiters)
3. If the skill's description, tags, or scope could apply — invoke it
4. Never skip a skill check because a task "seems simple"

## Development Pipeline (HARD-GATE Enforced)

All development MUST follow this sequence. No skipping steps.

```
brainstorming → writing-plans → subagent-driven-development → finishing-a-development-branch
```

### Gate Rules
- **HARD-GATE**: Design approval required before ANY implementation
- **TDD-GATE**: Tests must be written before code (RED → GREEN → REFACTOR)
- **REVIEW-GATE**: All changes must be reviewed against SPEC.md and PLAN.md

## Session Lifecycle

1. **Bootstrap**: Load `.superpowers/bootstrap.md` to initialize context
2. **Skill Check**: Run 1% Rule scan
3. **Plan Selection**: Load relevant PLAN.md, verify against SPEC.md
4. **Execution**: Follow skill-specific workflow
5. **Validation**: Run tests, verify against acceptance criteria
6. **Commit**: Git commit with conventional commit format

## Tool Mapping (Cross-Platform)

| Concept | Claude Code | Cursor | OpenCode | Codex | Gemini CLI | Copilot CLI |
|---------|-------------|--------|----------|-------|------------|-------------|
| Invoke Skill | `Skill` | `.cursor/skills/` | `activate_skill` | `/skills` | `/skills` | `@skill` |
| Read File | `Read` | Read file | `read_file` | Read | Read | Read |
| Write File | `Write` | Write file | `write_file` | Write | Write | Write |
| Run Command | `Bash` | Terminal | `execute_command` | Bash | Bash | Bash |
| Subagent | `Subtask` | Agent | `new_task` | Subagent | Subagent | Agent |

## TDD Enforcement

Every code change MUST follow:
1. **RED**: Write a failing test first
2. **GREEN**: Write minimal code to make it pass
3. **REFACTOR**: Clean up while keeping tests green

## File Structure

```
.superpowers/
├── bootstrap.md          # Session initialization
├── skills/
│   ├── SKILL.md          # This file — core system
│   ├── brainstorming.md   # Idea generation and exploration
│   ├── writing-plans.md   # Plan creation and SPEC alignment
│   ├── tdd.md            # Test-Driven Development workflow
│   ├── subagent-dev.md   # Subagent-driven development
│   └── finishing.md      # Branch completion and cleanup
└── workflows/
    └── default.yaml      # Default workflow configuration
```
