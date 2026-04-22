import os
from pathlib import Path
from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat
from agno.tools.shell import ShellTools
from agno.tools.file import FileTools
from agno.tools.mcp import MCPTools

from dotenv import load_dotenv

# Load environment variables from .env file first
load_dotenv()

# Configuration
WORKSPACE_ROOT = Path("devdep/workspace")
SUPERPOWERS_ROOT = Path("devdep/.superpowers")

# LLM Model (for chat/completions)
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gemma4:latest")

# Embedding Model (for vector search)
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "bge-m3:latest")

# Base URL for OpenAI-compatible API
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1")

# API Key (set to empty string for local endpoints that don't require auth)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "ollama")


def create_model() -> OpenAIChat:
    """Create an OpenAIChat model instance based on environment variables."""
    print(f"[Config] Using model: {OPENAI_MODEL}")
    print(f"[Config] Using base URL: {OPENAI_BASE_URL}")
    return OpenAIChat(
        id=OPENAI_MODEL,
        base_url=OPENAI_BASE_URL,
        api_key=OPENAI_API_KEY if OPENAI_API_KEY else None,
    )


# MCP Tools
context_mcp = MCPTools(
    command="npx -y @upstash/context7-mcp",
    env={"DEFAULT_MINIMUM_TOKENS": "1000"}
)

github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
github_mcp = None
if github_token:
    github_mcp = MCPTools(
        command="npx -y @modelcontextprotocol/server-github",
        env={"GITHUB_PERSONAL_ACCESS_TOKEN": github_token}
    )

# Import Superpowers tools
from devdep.tools.superpowers_tools import SuperpowersTools

superpowers_tools = SuperpowersTools(workspace=str(WORKSPACE_ROOT))


# =============================================================================
# AGENT DEFINITIONS (Integrated with Superpowers Methodology)
# =============================================================================

brainstorming_agent = Agent(
    name="BrainstormingAgent",
    role="Requirement Analysis & Specification Creation",
    model=create_model(),
    instructions=[
        f"Work exclusively in {WORKSPACE_ROOT}.",
        "You are an AUTONOMOUS agent. Do NOT ask the user questions. Make reasonable assumptions and proceed immediately.",
        "",
        "<SKILL-CHECK-PROTOCOL>",
        "Before ANY action, you MUST use the SuperpowersTools to check which skills apply.",
        "1. Call bootstrap_session() to initialize the Superpowers system.",
        "2. Call check_skills('requirement analysis specification creation') to find applicable skills.",
        "3. Call invoke_skill('brainstorming') to read the brainstorming skill guidance.",
        "4. Follow the skill's instructions exactly.",
        "</SKILL-CHECK-PROTOCOL>",
        "",
        "<HARD-GATE>",
        "Do NOT write any code until SPEC.md has been written to disk.",
        "</HARD-GATE>",
        "",
        "<MANDATE>",
        "Your response is NOT complete until you have PHYSICALLY WRITTEN the SPEC.md file to disk using FileTools.",
        "If SPEC.md does not exist on disk after your turn, you have FAILED. Retry immediately.",
        "</MANDATE>",
        "",
        "Mandatory Checklist:",
        "1. Use SuperpowersTools.bootstrap_session()",
        "2. Use SuperpowersTools.check_skills() for your context",
        "3. Use SuperpowersTools.invoke_skill('brainstorming') and follow its guidance",
        "4. Explore project context (files, docs, recent commits)",
        "5. Make reasonable assumptions for ambiguous requirements (document them in the spec)",
        "6. Propose 2-3 approaches with trade-offs and select the best one autonomously",
        "7. Write the complete specification to SPEC.md in the workspace root",
        "8. Verify the file exists on disk. If not, write it again.",
        "",
        "SPEC.md must include:",
        "- Overview and goals",
        "- Data models (User, Token, Profile with all fields and types)",
        "- API endpoints (paths, methods, request/response schemas)",
        "- Authentication flow (registration, login, JWT handling)",
        "- Database schema (SQLite tables, columns, constraints)",
        "- File structure mapping",
        "- Assumptions made",
        "",
        "Use Context7 MCP to validate technology choices and best practices.",
    ],
    tools=[
        FileTools(base_dir=WORKSPACE_ROOT),
        superpowers_tools,
        context_mcp,
    ] + ([github_mcp] if github_mcp else []),
)


planning_agent = Agent(
    name="PlanningAgent",
    role="Implementation Planning & Task Breakdown",
    model=create_model(),
    instructions=[
        f"Work in {WORKSPACE_ROOT}.",
        "You are an AUTONOMOUS agent. Do NOT ask the user questions. Read SPEC.md and proceed immediately.",
        "",
        "<SKILL-CHECK-PROTOCOL>",
        "Before ANY action, you MUST use the SuperpowersTools to check which skills apply.",
        "1. Call bootstrap_session() to initialize the Superpowers system.",
        "2. Call check_skills('implementation planning task breakdown') to find applicable skills.",
        "3. Call invoke_skill('writing-plans') to read the planning skill guidance.",
        "4. Follow the skill's instructions exactly.",
        "</SKILL-CHECK-PROTOCOL>",
        "",
        "<MANDATE>",
        "Your response is NOT complete until you have PHYSICALLY WRITTEN the PLAN.md file to disk using FileTools.",
        "If PLAN.md does not exist on disk after your turn, you have FAILED. Retry immediately.",
        "</MANDATE>",
        "",
        "1. Read SPEC.md from disk. If it does not exist, report failure and STOP.",
        "2. Use SuperpowersTools.evaluate_gate('hard-gate') to verify you can proceed.",
        "3. FILE-STRUCTURE-MAPPING FIRST: Map out ALL files to be created or modified.",
        "4. Break down implementation into bite-sized tasks (2-5 minutes each)",
        "5. Write the complete PLAN.md to the workspace root using FileTools",
        "6. EVERY task MUST include embedded TDD steps (RED -> GREEN -> REFACTOR)",
        "7. Ensure each task is self-contained and testable",
        "8. Identify dependencies between tasks",
        "9. NO PLACEHOLDERS allowed: 'TBD', 'implement later', `pass`, `# TODO` are plan failures",
        "10. Verify the file exists on disk. If not, write it again.",
        "",
        "Use Context7 MCP to find best practices for implementation patterns.",
    ],
    tools=[
        FileTools(base_dir=WORKSPACE_ROOT),
        superpowers_tools,
        context_mcp,
    ],
)


tdd_developer = Agent(
    name="TDDDeveloper",
    role="Test-Driven Development Implementation",
    model=create_model(),
    instructions=[
        f"Work in {WORKSPACE_ROOT}.",
        "You are an AUTONOMOUS agent. Do NOT ask the user questions. Read PLAN.md and implement tasks immediately.",
        "",
        "<SKILL-CHECK-PROTOCOL>",
        "Before ANY action, you MUST use the SuperpowersTools to check which skills apply.",
        "1. Call bootstrap_session() to initialize the Superpowers system.",
        "2. Call check_skills('test driven development implementation coding') to find applicable skills.",
        "3. Call invoke_skill('tdd') to read the TDD skill guidance.",
        "4. Follow the skill's instructions exactly.",
        "</SKILL-CHECK-PROTOCOL>",
        "",
        "<MANDATE>",
        "Your response is NOT complete until you have PHYSICALLY WRITTEN code files and test files to disk using FileTools.",
        "If files are not written to disk after your turn, you have FAILED. Retry immediately.",
        "</MANDATE>",
        "",
        "<IRON-LAW>",
        "NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST.",
        "If production code was written before its test exists and was observed failing, the code MUST be deleted.",
        "</IRON-LAW>",
        "",
        "<RUNNABLE-CODE-LAW>",
        "EVERY line of code you write MUST be runnable. The following are FORBIDDEN:",
        "- `pass` as a function body",
        "- `# TODO`, `FIXME`, `XXX` comments",
        "- `raise NotImplementedError` or `...` as implementation",
        "- Empty functions, empty classes, or stub methods",
        "- Broken imports (importing a module/file that does not exist)",
        "</RUNNABLE-CODE-LAW>",
        "",
        "1. Read PLAN.md from disk. If it does not exist, report failure and STOP.",
        "2. Use SuperpowersTools.evaluate_gate('tdd-gate') before writing code.",
        "3. RED: Write ONE minimal failing test. Requirements:",
        "   - One behavior per test",
        "   - Clear name describing behavior",
        "   - Real code, not mocks",
        "   - Write the test to disk BEFORE running it",
        "4. VERIFY RED: Run the test suite using ShellTools and confirm it FAILS for the expected reason.",
        "5. GREEN: Write the SIMPLEST code that makes the test pass.",
        "6. VERIFY GREEN: Run the FULL test suite and confirm all tests pass.",
        "7. REFACTOR: Only after GREEN, improve code quality. Re-run tests after every change.",
        "8. Commit working code with descriptive commit messages.",
        "9. FINAL VERIFICATION: Start the application and test at least one endpoint.",
        "",
        "Use ShellTools to execute 'pytest' for testing and 'uvicorn' for server verification.",
    ],
    tools=[
        FileTools(base_dir=WORKSPACE_ROOT),
        ShellTools(base_dir=WORKSPACE_ROOT),
        superpowers_tools,
        context_mcp,
    ] + ([github_mcp] if github_mcp else []),
)


review_agent = Agent(
    name="ReviewAgent",
    role="Quality Assurance & Code Review",
    model=create_model(),
    instructions=[
        f"Work in {WORKSPACE_ROOT}.",
        "You are an AUTONOMOUS agent. Do NOT ask the user questions. Read the code and produce the review immediately.",
        "",
        "<SKILL-CHECK-PROTOCOL>",
        "Before ANY action, you MUST use the SuperpowersTools to check which skills apply.",
        "1. Call bootstrap_session() to initialize the Superpowers system.",
        "2. Call check_skills('quality assurance code review finishing') to find applicable skills.",
        "3. Call invoke_skill('finishing') to read the finishing skill guidance.",
        "4. Follow the skill's instructions exactly.",
        "</SKILL-CHECK-PROTOCOL>",
        "",
        "<MANDATE>",
        "Your response is NOT complete until you have PHYSICALLY WRITTEN the REVIEW.md file to disk using FileTools.",
        "If REVIEW.md does not exist on disk after your turn, you have FAILED. Retry immediately.",
        "</MANDATE>",
        "",
        "1. Read SPEC.md and PLAN.md from disk. If they do not exist, report failure and STOP.",
        "2. Use SuperpowersTools.evaluate_gate('review-gate') to verify review criteria.",
        "",
        "STAGE 1 - Spec Compliance Review (MUST pass before Stage 2):",
        "1. Compare implementation against SPEC.md and PLAN.md",
        "2. Verify ALL requirements are met - nothing more, nothing less",
        "3. Check for missing functionality and scope creep",
        "4. If Stage 1 fails: STOP. Report issues by severity:",
        "   - Critical (Must Fix): Bugs, security issues, data loss risks",
        "   - Important (Should Fix): Architecture problems, missing features, test gaps",
        "   - Minor (Nice to Have): Code style, documentation improvements",
        "",
        "STAGE 2 - Code Quality Review (only after Stage 1 passes):",
        "1. Validate code follows best practices (separation of concerns, DRY, YAGNI)",
        "2. Ensure comprehensive test coverage (>90%) with REAL tests",
        "3. Check for code smells and optimization opportunities",
        "4. Validate database integrity and schema compliance",
        "",
        "Review Output Format (write to REVIEW.md):",
        "Strengths: [what was done well]",
        "Issues:",
        "  Critical (Must Fix): [list]",
        "  Important (Should Fix): [list]",
        "  Minor (Nice to Have): [list]",
        "Assessment: [Ready to merge | With fixes | No]",
        "",
        "Use ShellTools to execute 'pytest' for testing and 'sqlite3' commands for database inspection.",
        "Only approve when BOTH review stages pass.",
    ],
    tools=[
        FileTools(base_dir=WORKSPACE_ROOT),
        ShellTools(base_dir=WORKSPACE_ROOT),
        superpowers_tools,
    ],
)


# =============================================================================
# TEAM ORCHESTRATION
# =============================================================================

superpowers_team = Team(
    members=[brainstorming_agent, planning_agent, tdd_developer, review_agent],
    model=create_model(),
    instructions=[
        f"All work happens in {WORKSPACE_ROOT}.",
        "",
        "<EXTREMELY-IMPORTANT>",
        "If you think there is even a 1% chance a skill might apply to what you are doing, you ABSOLUTELY MUST invoke the skill.",
        "IF A SKILL APPLIES TO YOUR TASK, YOU DO NOT HAVE A CHOICE. YOU MUST USE IT.",
        "This is not negotiable. This is not optional.",
        "</EXTREMELY-IMPORTANT>",
        "",
        "<AUTONOMOUS-MODE>",
        "You are running in FULLY AUTONOMOUS mode. Do NOT ask the user for input.",
        "Make reasonable assumptions and proceed immediately through the entire workflow.",
        "If an agent asks clarifying questions, answer them yourself with reasonable defaults and re-delegate.",
        "</AUTONOMOUS-MODE>",
        "",
        "<FILE-GATE>",
        "The workflow is FILE-DRIVEN. Each phase MUST produce a physical file on disk before proceeding:",
        "- Phase 1: BrainstormingAgent MUST write SPEC.md to disk.",
        "- Phase 2: PlanningAgent MUST write PLAN.md to disk.",
        "- Phase 3: TDDDeveloper MUST write code and test files to disk.",
        "- Phase 4: ReviewAgent MUST write REVIEW.md to disk.",
        "NEVER proceed to the next phase until the current phase's file(s) are confirmed on disk.",
        "</FILE-GATE>",
        "",
        "<RUNNABLE-GATE>",
        "Code is only considered complete when it is RUNNABLE. Before finishing Phase 3, verify ALL of the following:",
        "- `python -c 'import main'` executes without ImportError",
        "- `uvicorn main:app --reload` starts the FastAPI server without crashing",
        "- No file contains `pass`, `# TODO`, `...`, or `raise NotImplementedError` as implementation",
        "- Every import in every file resolves to an existing module",
        "- `SQLModel.metadata.create_all(engine)` is called during startup",
        "- `app = FastAPI()` exists in the main entry point",
        "- API endpoints are actually registered. Test with `curl http://127.0.0.1:8000/docs`",
        "- Tests exist on disk and have been executed with `pytest`",
        "If any check fails, the TDDDeveloper MUST fix it before the phase is considered complete.",
        "</RUNNABLE-GATE>",
        "",
        "Follow the complete Superpowers methodology workflow:",
        "1. Delegate to BrainstormingAgent to create SPEC.md. Verify file exists.",
        "2. Delegate to PlanningAgent to create PLAN.md from SPEC.md. Verify file exists.",
        "3. Delegate to TDDDeveloper to implement tasks from PLAN.md. Verify code files exist.",
        "4. Delegate to ReviewAgent to review implementation. Verify REVIEW.md exists.",
        "",
        "Execution Mode: Subagent-Driven Development (SDD)",
        "- The controller reads the plan ONCE at the start and extracts all tasks",
        "- For EACH task, dispatch a FRESH subagent with isolated context",
        "- After each task: Two-stage review (Spec Compliance -> Code Quality)",
        "- Model selection strategy:",
        "  * Mechanical tasks (1-2 files, clear spec): use fast/cheap model",
        "  * Integration tasks (multi-file): use standard model",
        "  * Architecture/review tasks: use most capable model",
        "- Implementer status protocol: DONE, DONE_WITH_CONCERNS, BLOCKED, NEEDS_CONTEXT",
        "- If BLOCKED: assess whether to provide context, upgrade model, break task down, or escalate to human",
        "",
        "The team uses Context7 for research and GitHub for code references.",
        "The goal is a robust system based on SQLite.",
        "Maintain strict separation of concerns between agents.",
        "Ensure all artifacts are persisted to the workspace.",
    ],
    show_members_responses=True,
    markdown=True,
)

if __name__ == "__main__":
    superpowers_team.print_response(
        "Build a complete User Management System with FastAPI and SQLite. "
        "Include user registration, authentication, and profile management. "
        "Follow the complete Superpowers methodology with specification, planning, TDD implementation, and review.",
        stream=True
    )
