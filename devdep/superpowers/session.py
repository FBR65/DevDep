"""
Superpowers Session Lifecycle Manager.

Handles bootstrap, skill checks, planning, development, and finishing phases.
"""

import os
from pathlib import Path
from typing import Optional

from .skills import SkillRegistry, Skill
from .gates import GateKeeper


class SuperpowersSession:
    """
    Manages a complete Superpowers development session.

    Usage:
        session = SuperpowersSession()
        session.bootstrap()
        session.run_skill_check("I need to implement user authentication")
        session.evaluate_gate("hard-gate")
    """

    def __init__(self, workspace: str = "devdep/workspace"):
        self.workspace = Path(workspace)
        self.skills = SkillRegistry()
        self.gates = GateKeeper()
        self.state: str = "uninitialized"
        self.active_skills: list[Skill] = []
        self.log: list[str] = []

    def bootstrap(self) -> None:
        """
        Initialize the session by loading bootstrap.md and discovering skills.
        """
        self._log("=" * 60)
        self._log("SUPERPOWERS SESSION BOOTSTRAP")
        self._log("=" * 60)

        # 1. Load bootstrap configuration
        bootstrap_path = Path("devdep/.superpowers/bootstrap.md")
        if bootstrap_path.exists():
            self._log(f"Loading bootstrap: {bootstrap_path}")
        else:
            self._log("WARNING: No bootstrap.md found, using defaults")

        # 2. Discover skills
        self._log(f"Discovered {len(self.skills.skills)} skills:")
        for skill in self.skills.list_skills():
            self._log(f"  - {skill.slug}: {skill.name}")

        # 3. Load project context
        spec_path = self.workspace / "SPEC.md"
        plan_path = self.workspace / "PLAN.md"

        if spec_path.exists():
            self._log(f"SPEC.md loaded: {spec_path}")
        else:
            self._log("WARNING: No SPEC.md found")

        if plan_path.exists():
            self._log(f"PLAN.md loaded: {plan_path}")
            self.state = "planning"
        else:
            self._log("No PLAN.md found — session starts in brainstorming state")
            self.state = "brainstorming"

        # 4. Determine state
        self._assess_state()
        self._log(f"Session state: {self.state}")
        self._log("=" * 60)

    def _assess_state(self) -> None:
        """Determine the current session state based on files and gates."""
        plan_path = self.workspace / "PLAN.md"

        if not plan_path.exists():
            self.state = "brainstorming"
            return

        plan_content = plan_path.read_text()

        # Check if plan has unchecked tasks
        import re
        unchecked = re.findall(r"^\s*-\s*\[ \]", plan_content, re.MULTILINE)
        checked = re.findall(r"^\s*-\s*\[x\]", plan_content, re.MULTILINE)

        if unchecked and not checked:
            self.state = "planning"  # Plan exists but not started
        elif unchecked and checked:
            self.state = "development"  # In progress
        elif checked and not unchecked:
            self.state = "finishing"  # Ready to finish
        else:
            self.state = "brainstorming"

    def run_skill_check(self, context: str) -> list[Skill]:
        """
        Apply the 1% Rule: find all skills that apply to the context.
        """
        self._log(f"\nRunning 1% Rule skill check for: '{context}'")
        applicable = self.skills.check_1_percent_rule(context)

        if applicable:
            self._log(f"Found {len(applicable)} applicable skills:")
            for skill in applicable:
                self._log(f"  → {skill.slug}: {skill.name}")
        else:
            self._log("No skills triggered (this is rare — check your context)")

        self.active_skills = applicable
        return applicable

    def invoke_skill(self, slug: str) -> str:
        """Invoke a specific skill and return its guidance."""
        self._log(f"\nInvoking skill: {slug}")
        content = self.skills.invoke(slug)
        self._log(f"Skill '{slug}' loaded successfully")
        return content

    def evaluate_gate(self, gate_name: str) -> bool:
        """Evaluate a gate and print its report."""
        self._log(f"\nEvaluating gate: {gate_name}")
        report = self.gates.report(gate_name)
        self._log(report)
        return self.gates.check(gate_name)

    def transition(self, new_state: str) -> None:
        """Transition to a new session state."""
        valid_states = ["brainstorming", "planning", "development", "finishing", "complete"]
        if new_state not in valid_states:
            raise ValueError(f"Invalid state: {new_state}. Must be one of {valid_states}")

        self._log(f"\nState transition: {self.state} → {new_state}")
        self.state = new_state

    def get_recommended_skill(self) -> Optional[str]:
        """Get the recommended skill for the current state."""
        state_skill_map = {
            "brainstorming": "brainstorming",
            "planning": "writing-plans",
            "development": "subagent-dev",
            "finishing": "finishing",
        }
        return state_skill_map.get(self.state)

    def _log(self, message: str) -> None:
        """Log a message to the session log."""
        self.log.append(message)
        print(message)

    def get_log(self) -> str:
        """Get the full session log."""
        return "\n".join(self.log)
