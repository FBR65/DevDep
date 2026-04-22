# Developer Department (DevDep)

An autonomous software development team powered by Agno agents following the Superpowers methodology, integrated with MCP servers for enhanced capabilities.

## Overview

This project implements a complete developer department setup using:
- **Agno agents** for orchestration (Brainstorming, Planning, TDD Development, Review)
- **Superpowers methodology** for disciplined development practices (skills, gates, TDD)
- **MCP integration** with Context7 and GitHub for extended knowledge
- **Docker containers** for isolated development environments
- **uv package manager** for fast dependency management
- **SQLite database** for lightweight data persistence

## Architecture

```
devdep/
├── main.py                    # Agno orchestrator: 4-agent team with Superpowers integration
├── tools/
│   ├── __init__.py
│   └── superpowers_tools.py   # Agno Toolkit wrapping Superpowers methodology
├── superpowers/               # Superpowers runtime engine (Python)
│   ├── __init__.py
│   ├── __main__.py            # CLI entry point
│   ├── session.py             # Session lifecycle manager
│   ├── skills.py              # Skill discovery & 1% Rule matching
│   └── gates.py               # Gate evaluation (HARD-GATE, TDD-GATE, REVIEW-GATE)
├── .superpowers/              # Superpowers configuration (skills, workflows)
│   ├── bootstrap.md           # Session initialization protocol
│   ├── skills/
│   │   ├── SKILL.md           # Core system (1% Rule, pipeline, gates)
│   │   ├── brainstorming.md   # Idea exploration skill
│   │   ├── writing-plans.md   # Plan creation with HARD-GATE
│   │   ├── tdd.md             # RED-GREEN-REFACTOR enforcement
│   │   ├── subagent-dev.md    # Subagent delegation skill
│   │   └── finishing.md       # Branch completion & quality gates
│   └── workflows/
│       └── default.yaml       # Pipeline: bootstrap → check → plan → develop → test → finish
├── workspace/                 # Generated code and artifacts
│   ├── SPEC.md                # Project specification (written by BrainstormingAgent)
│   ├── PLAN.md                # Implementation plan (written by PlanningAgent)
│   ├── REVIEW.md              # Code review (written by ReviewAgent)
│   ├── main.py                # FastAPI application
│   ├── models.py              # SQLModel database models
│   ├── schemas.py             # Pydantic request/response schemas
│   ├── crud.py                # Database operations
│   └── database.py            # SQLite engine & session management
├── Dockerfile                 # Docker configuration
├── docker-compose.yml         # Docker Compose configuration
├── .env.example               # Environment variables template
└── init.sh                    # Initialization script
```

## Features

### 1. Multi-Agent Team Structure
Each agent is integrated with the Superpowers methodology via `SuperpowersTools`:

| Agent | Role | Superpowers Skill |
|-------|------|-------------------|
| **BrainstormingAgent** | Requirement analysis and specification creation | `brainstorming` |
| **PlanningAgent** | System architecture and task breakdown | `writing-plans` |
| **TDDDeveloper** | Test-driven development implementation | `tdd` |
| **ReviewAgent** | Testing and quality assurance | `finishing` |

### 2. Superpowers Methodology Integration

**The 1% Rule**: If there's even a 1% chance a skill applies to a task, it MUST be invoked.

**Development Pipeline** (HARD-GATE enforced):
```
brainstorming → writing-plans → subagent-driven-development → finishing
```

**Gates**:
- **HARD-GATE**: Design approval required before ANY implementation
- **TDD-GATE**: Tests must pass before proceeding (RED → GREEN → REFACTOR)
- **REVIEW-GATE**: Code review against SPEC.md and PLAN.md

**Skills** (declarative markdown in `.superpowers/skills/`):
- Each skill has YAML frontmatter with triggers, description, and scope
- Agents invoke skills via `SuperpowersTools.check_skills()` and `invoke_skill()`
- Skills provide structured guidance that agents follow exactly

### 3. MCP Server Integration
- **Context7** for framework documentation and best practices
- **GitHub MCP** for code reference and repository analysis

### 4. Dockerized Environment
- Isolated development environment
- Persistent workspace through volume mapping
- Pre-installed tools and dependencies

## Setup Instructions

### 1. Clone the repository
```bash
git clone <repository-url>
cd devdep
```

### 2. Install uv package manager
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. Copy and configure environment variables
```bash
cp devdep/.env.example .env
# Edit .env file with your actual API keys
```

### 4. Install dependencies
```bash
uv sync
```

## Usage

### Method 1: Agno Agent Team (Autonomous)

Run the full autonomous agent team as described in the README:

```bash
uv run python devdep/main.py
```

The agent team will:
1. **BrainstormingAgent**: Analyze requirements and write `SPEC.md`
2. **PlanningAgent**: Create `PLAN.md` with TDD steps from `SPEC.md`
3. **TDDDeveloper**: Implement code following RED-GREEN-REFACTOR
4. **ReviewAgent**: Review implementation and write `REVIEW.md`

Each agent automatically invokes Superpowers skills and evaluates gates before acting.

### Method 2: Superpowers CLI (Manual)

Use the CLI for manual skill invocation and gate evaluation:

```bash
# Initialize session and discover skills
uv run superpowers bootstrap

# Check which skills apply to your task
uv run superpowers check "I need to implement JWT authentication"

# Invoke a skill to read its guidance
uv run superpowers invoke tdd

# Evaluate a gate before proceeding
uv run superpowers gate hard-gate

# List all available skills
uv run superpowers skills

# Show current session state
uv run superpowers state
```

### Method 3: FastAPI App (Direct)

Run the workspace application directly:

```bash
cd devdep/workspace
uv run python main.py
```

Or with uvicorn:
```bash
cd devdep/workspace
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Compose

```bash
docker-compose -f devdep/docker-compose.yml up --build
```

## How the Superpowers Integration Works

### Agent Skill Protocol
Every agent follows this protocol before any action:

1. **Bootstrap**: `SuperpowersTools.bootstrap_session()`
   - Discovers all skills in `.superpowers/skills/`
   - Loads `SPEC.md` and `PLAN.md`
   - Assesses current session state

2. **1% Rule Check**: `SuperpowersTools.check_skills(context)`
   - Analyzes task context against all skill metadata
   - Returns ALL skills that could apply (even 1% chance)

3. **Skill Invocation**: `SuperpowersTools.invoke_skill(skill_slug)`
   - Loads full skill markdown content
   - Agent follows the skill's instructions exactly

4. **Gate Evaluation**: `SuperpowersTools.evaluate_gate(gate_name)`
   - Verifies prerequisites before proceeding
   - Blocks if checks fail

### Example: TDDDeveloper Workflow
```
1. bootstrap_session() → discovers skills, loads PLAN.md
2. check_skills("implement user authentication with JWT") → returns [tdd, writing-plans]
3. invoke_skill("tdd") → reads RED-GREEN-REFACTOR cycle instructions
4. evaluate_gate("tdd-gate") → checks if failing test exists
5. Writes failing test (RED)
6. Writes minimal code to pass (GREEN)
7. Refactors while keeping tests green
8. evaluate_gate("tdd-gate") → confirms all tests pass
```

## Customization

### Agent Behaviors
Modify `devdep/main.py` to customize:
- Agent instructions and roles
- Model selection per agent
- Tool configurations

### Superpowers Skills
Add new skills by creating `.md` files in `devdep/.superpowers/skills/`:
```markdown
---
skill: my-skill
name: My Custom Skill
description: What this skill does
triggers:
  - keyword1
  - keyword2
---

# My Custom Skill

## Instructions
...
```

### Workflows
Modify `devdep/.superpowers/workflows/default.yaml` to change the pipeline.

## Requirements

- Python >= 3.11
- Docker and Docker Compose (optional)
- OpenAI API key (or local Ollama endpoint)
- (Optional) GitHub Personal Access Token for extended GitHub access

## License

This project is licensed under the MIT License - see the LICENSE file for details.
