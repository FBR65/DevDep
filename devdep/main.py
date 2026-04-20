import os
from agno.agent import Agent
from agno.agent.team import AgentTeam
from agno.models.openai import OpenAIChat
from agno.tools.shell import ShellTools
from agno.tools.file import FileTools
from agno.tools.mcp import McpTools

# Configuration
WORKSPACE_ROOT = "/app/workspace"

# MCP Tools
# Context7 from Upstash (Keyless for Docs)
context_mcp = McpTools(
    command="npx",
    args=["-y", "@upstash/context7-mcp"],
    env={"DEFAULT_MINIMUM_TOKENS": "1000"}
)

# GitHub MCP (Requires token for stable limits, fallback to Git CLI)
github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
github_mcp = None
if github_token:
    github_mcp = McpTools(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-github"],
        env={"GITHUB_PERSONAL_ACCESS_TOKEN": github_token}
    )

# Superpowers Agent Roles

# 1. Brainstorming Agent (Product Owner)
# Responsible for requirement analysis and specification creation
brainstorming_agent = Agent(
    name="BrainstormingAgent",
    role="Requirement Analysis & Specification Creation",
    model=OpenAIChat(id="gpt-4o"),
    instructions=[
        f"Work exclusively in {WORKSPACE_ROOT}.",
        "Follow the Superpowers Brainstorming methodology:",
        "1. Analyze project context (files, documentation, recent commits)",
        "2. Ask clarifying questions one at a time to fully understand requirements",
        "3. Propose 2-3 potential approaches with trade-off analysis",
        "4. Create detailed specification documents in SPEC.md",
        "5. Implement a spec review loop with subagent reviewers",
        "6. Only proceed to planning after spec approval",
        "Use Context7 MCP to validate technology choices and best practices.",
        "If you need to analyze public repositories, use ShellTools with 'git clone' if GitHub MCP is not available."
    ],
    tools=[FileTools(base_dir=WORKSPACE_ROOT), context_mcp] + ([github_mcp] if github_mcp else []),
)

# 2. Planning Agent (Tech Lead)
# Responsible for creating detailed implementation plans
planning_agent = Agent(
    name="PlanningAgent",
    role="Implementation Planning & Task Breakdown",
    model=OpenAIChat(id="gpt-4o"),
    instructions=[
        f"Work in {WORKSPACE_ROOT}.",
        "Follow the Superpowers Planning methodology:",
        "1. Read and analyze the approved specification document (SPEC.md)",
        "2. Break down implementation into small, manageable tasks",
        "3. Create a detailed PLAN.md file with sequential tasks",
        "4. Ensure each task is self-contained and testable",
        "5. Identify dependencies between tasks",
        "6. Estimate complexity and duration for each task",
        "Use 'query-docs' via Context7 to find best practices for implementation patterns.",
        "Design clean SQLite schema and overall system architecture."
    ],
    tools=[FileTools(base_dir=WORKSPACE_ROOT), context_mcp],
)

# 3. TDD Developer Agent
# Responsible for implementing tasks with Test-Driven Development
tdd_developer = Agent(
    name="TDDDeveloper",
    role="Test-Driven Development Implementation",
    model=OpenAIChat(id="gpt-4o"),
    instructions=[
        f"Work in {WORKSPACE_ROOT}.",
        "Follow the Superpowers TDD methodology (Red-Green-Refactor):",
        "1. Read the current task from PLAN.md",
        "2. RED: Write a failing test that validates the task requirements",
        "3. GREEN: Write minimal code to make the test pass",
        "4. REFACTOR: Improve code quality while keeping tests passing",
        "5. Verify all existing tests still pass",
        "6. Commit working code with descriptive commit messages",
        "If you need code references and GitHub MCP is not available, use 'git clone' via Shell.",
        "Write clean code with FastAPI and SQLite.",
        "Always write tests first, then implementation."
    ],
    tools=[FileTools(base_dir=WORKSPACE_ROOT), ShellTools(base_dir=WORKSPACE_ROOT), context_mcp] + ([github_mcp] if github_mcp else []),
)

# 4. Review Agent (QA Engineer)
# Responsible for reviewing implementation quality and compliance
review_agent = Agent(
    name="ReviewAgent",
    role="Quality Assurance & Code Review",
    model=OpenAIChat(id="gpt-4o"),
    instructions=[
        f"Work in {WORKSPACE_ROOT}.",
        "Follow the Superpowers Review methodology (Two-stage review):",
        "Stage 1 - Spec Compliance Review:",
        "1. Compare implementation against the original specification",
        "2. Verify all requirements are met",
        "3. Check for missing functionality",
        "Stage 2 - Code Quality Review:",
        "1. Validate code follows best practices",
        "2. Ensure comprehensive test coverage (>90%)",
        "3. Check for code smells and optimization opportunities",
        "4. Validate database integrity and schema compliance",
        "Use ShellTools to execute 'pytest' for testing and 'sqlite3' commands for database inspection.",
        "Provide constructive feedback to developers for improvements.",
        "Only approve when both review stages pass."
    ],
    tools=[FileTools(base_dir=WORKSPACE_ROOT), ShellTools(base_dir=WORKSPACE_ROOT)],
)

# Superpowers Team Orchestration
superpowers_team = AgentTeam(
    agents=[brainstorming_agent, planning_agent, tdd_developer, review_agent],
    instructions=[
        f"All work happens in {WORKSPACE_ROOT}.",
        "Follow the complete Superpowers methodology workflow:",
        "1. Brainstorming Agent creates specifications (SPEC.md)",
        "2. Planning Agent creates implementation plans (PLAN.md)",
        "3. TDD Developer implements tasks following Red-Green-Refactor",
        "4. Review Agent conducts two-stage review process",
        "The team uses Context7 for research and GitHub for code references.",
        "The goal is a robust system based on SQLite.",
        "Maintain strict separation of concerns between agents.",
        "Ensure all artifacts are persisted to the workspace."
    ],
    show_tool_calls=True,
    markdown=True,
)

if __name__ == "__main__":
    # Example usage
    superpowers_team.print_response(
        "Build a complete User Management System with FastAPI and SQLite. "
        "Include user registration, authentication, and profile management. "
        "Follow the complete Superpowers methodology with specification, planning, TDD implementation, and review.",
        stream=True
    )