"""
Agno-compatible tool wrapper for the Superpowers methodology system.

Provides agents with access to:
- Skill discovery and invocation (1% Rule)
- Gate evaluation (HARD-GATE, TDD-GATE, REVIEW-GATE)
- Session state tracking
- Bootstrap initialization
"""

import subprocess
from pathlib import Path
from typing import Optional

from agno.tools import Toolkit

from devdep.superpowers.session import SuperpowersSession
from devdep.superpowers.skills import SkillRegistry
from devdep.superpowers.gates import GateKeeper


class SuperpowersTools(Toolkit):
    """
    Toolkit that exposes Superpowers methodology to Agno agents.

    Agents use these tools to:
    1. Check which skills apply to their current task (1% Rule)
    2. Invoke skills to get structured guidance
    3. Evaluate gates before proceeding
    4. Track session state
    """

    def __init__(self, workspace: str = "devdep/workspace"):
        super().__init__(name="superpowers_tools")
        self.workspace = Path(workspace)
        self.session: Optional[SuperpowersSession] = None
        self._registry = SkillRegistry()
        self._gates = GateKeeper()

        # Register all tools with Agno
        self.register(self.bootstrap_session)
        self.register(self.check_skills)
        self.register(self.invoke_skill)
        self.register(self.evaluate_gate)
        self.register(self.get_session_state)
        self.register(self.list_all_skills)
        self.register(self.read_skill_content)
        self.register(self.write_file)
        self.register(self.read_file)
        # Single-parameter file writers for reliable agent usage
        self.register(self.write_spec)
        self.register(self.write_plan)
        self.register(self.write_review)
        self.register(self.write_code_file)
        self.register(self.write_test_file)

    def bootstrap_session(self) -> str:
        """
        Initialize a Superpowers session.
        Discovers skills, loads SPEC.md/PLAN.md, and assesses current state.
        Must be called before any other Superpowers tool.
        """
        self.session = SuperpowersSession(workspace=str(self.workspace))
        self.session.bootstrap()
        return self.session.get_log()

    def check_skills(self, context: str) -> str:
        """
        Apply the 1% Rule: find all skills that apply to the given context.
        If there's even a 1% chance a skill applies, it MUST be invoked.

        Args:
            context: Description of the current task or problem
        """
        if not self.session:
            return "ERROR: Session not bootstrapped. Call bootstrap_session() first."

        applicable = self.session.run_skill_check(context)
        if not applicable:
            return "No skills triggered. This is rare — verify your context describes the task clearly."

        lines = [f"Found {len(applicable)} applicable skills:"]
        for skill in applicable:
            lines.append(f"  - {skill.slug}: {skill.name}")
            lines.append(f"    Description: {skill.description[:100]}...")
        lines.append("\nInvoke a skill with invoke_skill(skill_slug) to read its full guidance.")
        return "\n".join(lines)

    def invoke_skill(self, skill_slug: str) -> str:
        """
        Invoke a specific skill and return its full guidance content.

        Args:
            skill_slug: The skill identifier (e.g., 'tdd', 'writing-plans', 'brainstorming')
        """
        if not self.session:
            return "ERROR: Session not bootstrapped. Call bootstrap_session() first."

        try:
            content = self.session.invoke_skill(skill_slug)
            return content
        except ValueError as e:
            available = ", ".join(self.session.skills.skills.keys())
            return f"ERROR: {e}\nAvailable skills: {available}"

    def evaluate_gate(self, gate_name: str) -> str:
        """
        Evaluate a development gate and return its report.
        Gates block progress until all checks pass.

        Args:
            gate_name: One of 'hard-gate', 'tdd-gate', 'review-gate'
        """
        if not self.session:
            return "ERROR: Session not bootstrapped. Call bootstrap_session() first."

        try:
            report = self.session.evaluate_gate(gate_name)
            passed = self.session.gates.check(gate_name)
            status = "PASSED" if passed else "BLOCKED"
            return f"{report}\n\nGate Status: {status}"
        except ValueError as e:
            return f"ERROR: {e}"

    def get_session_state(self) -> str:
        """
        Get the current session state and recommended next skill.
        States: brainstorming, planning, development, finishing, complete
        """
        if not self.session:
            return "ERROR: Session not bootstrapped. Call bootstrap_session() first."

        recommended = self.session.get_recommended_skill()
        return (
            f"Current state: {self.session.state}\n"
            f"Recommended skill: {recommended or 'None'}\n"
            f"Active skills: {[s.slug for s in self.session.active_skills]}"
        )

    def list_all_skills(self) -> str:
        """
        List all available Superpowers skills with their descriptions.
        """
        skills = self._registry.list_skills()
        lines = [f"Available skills ({len(skills)}):"]
        for skill in skills:
            lines.append(f"  {skill.slug:20s} - {skill.name}")
            lines.append(f"    {skill.description[:80]}...")
        return "\n".join(lines)

    def read_skill_content(self, skill_slug: str) -> str:
        """
        Read the raw markdown content of a skill file.
        Use this when you need the full skill text for your instructions.

        Args:
            skill_slug: The skill identifier
        """
        skill = self._registry.get(skill_slug)
        if not skill:
            available = ", ".join(self._registry.skills.keys())
            return f"ERROR: Skill '{skill_slug}' not found. Available: {available}"

        if skill.filepath:
            return skill.filepath.read_text(encoding="utf-8")
        return skill.content

    def write_file(self, file_name: str, contents: str) -> str:
        """
        Write contents to a file in the workspace.
        This is a reliable alternative to FileTools.save_file.

        Args:
            file_name: Relative path within the workspace (e.g. 'SPEC.md')
            contents: The full file content to write
        """
        target = self.workspace / file_name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(contents, encoding="utf-8")
        return f"Successfully wrote {target} ({len(contents)} chars)"

    def read_file(self, file_name: str) -> str:
        """
        Read the contents of a file from the workspace.
        This is a reliable alternative to FileTools.read_file.

        Args:
            file_name: Relative path within the workspace (e.g. 'SPEC.md')
        """
        target = self.workspace / file_name
        if not target.exists():
            return f"ERROR: File not found: {target}"
        return target.read_text(encoding="utf-8")

    # ------------------------------------------------------------------
    # Single-parameter file writers (model-friendly)
    # ------------------------------------------------------------------

    def write_spec(self, contents: str) -> str:
        """Write the SPEC.md file. Only requires the file contents."""
        return self.write_file("SPEC.md", contents)

    def write_plan(self, contents: str) -> str:
        """Write the PLAN.md file. Only requires the file contents."""
        return self.write_file("PLAN.md", contents)

    def write_review(self, contents: str) -> str:
        """Write the REVIEW.md file. Only requires the file contents."""
        return self.write_file("REVIEW.md", contents)

    def write_code_file(self, file_name: str, contents: str) -> str:
        """
        Write a production code file. Requires file_name and contents.
        Example: write_code_file(file_name='main.py', contents='...')
        """
        return self.write_file(file_name, contents)

    def write_test_file(self, file_name: str, contents: str) -> str:
        """
        Write a test file. Requires file_name and contents.
        Example: write_test_file(file_name='tests/test_auth.py', contents='...')
        """
        return self.write_file(file_name, contents)
