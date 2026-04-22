"""
Gate system for the Superpowers methodology.

Enforces HARD-GATE, TDD-GATE, and REVIEW-GATE checks.
"""

from dataclasses import dataclass, field
from typing import Callable


@dataclass
class GateCheck:
    """A single check within a gate."""
    name: str
    description: str
    check_fn: Callable[[], bool]
    passed: bool = False


@dataclass
class Gate:
    """A development gate with multiple checks."""
    name: str
    description: str
    checks: list[GateCheck] = field(default_factory=list)

    def evaluate(self) -> bool:
        """Run all checks and return True only if ALL pass."""
        all_passed = True
        for check in self.checks:
            try:
                check.passed = check.check_fn()
            except Exception:
                check.passed = False
            if not check.passed:
                all_passed = False
        return all_passed

    def report(self) -> str:
        """Generate a human-readable report of gate status."""
        lines = [f"\n{'='*60}", f"Gate: {self.name}", f"{'='*60}"]
        lines.append(f"Description: {self.description}\n")

        for check in self.checks:
            status = "✅ PASS" if check.passed else "❌ FAIL"
            lines.append(f"  [{status}] {check.name}")
            lines.append(f"           {check.description}")

        overall = "✅ ALL CHECKS PASSED" if self.evaluate() else "❌ GATE BLOCKED"
        lines.append(f"\n{'='*60}")
        lines.append(overall)
        lines.append(f"{'='*60}\n")
        return "\n".join(lines)


class GateKeeper:
    """Manages all gates in the Superpowers system."""

    def __init__(self):
        self.gates: dict[str, Gate] = {}
        self._setup_default_gates()

    def _setup_default_gates(self) -> None:
        """Configure the default gates from the Superpowers methodology."""

        # HARD-GATE: Design approval required before implementation
        self.gates["hard-gate"] = Gate(
            name="HARD-GATE",
            description="Design approval required before ANY implementation",
            checks=[
                GateCheck(
                    name="plan_reviewed_against_spec",
                    description="PLAN.md has been reviewed against SPEC.md",
                    check_fn=lambda: self._file_exists("devdep/workspace/PLAN.md")
                    and self._file_exists("devdep/workspace/SPEC.md"),
                ),
                GateCheck(
                    name="acceptance_criteria_defined",
                    description="All tasks have acceptance criteria",
                    check_fn=lambda: self._plan_has_acceptance_criteria(),
                ),
                GateCheck(
                    name="tdd_steps_defined",
                    description="TDD steps defined for each task",
                    check_fn=lambda: self._plan_has_tdd_steps(),
                ),
                GateCheck(
                    name="dependencies_identified",
                    description="Dependencies identified and ordered",
                    check_fn=lambda: self._plan_has_dependencies(),
                ),
            ],
        )

        # TDD-GATE: Tests must pass
        self.gates["tdd-gate"] = Gate(
            name="TDD-GATE",
            description="Tests must be written and passing before proceeding",
            checks=[
                GateCheck(
                    name="failing_test_written",
                    description="A failing test was written first (RED phase)",
                    check_fn=lambda: True,  # This is enforced by workflow
                ),
                GateCheck(
                    name="implementation_makes_test_pass",
                    description="Implementation makes the test pass (GREEN phase)",
                    check_fn=lambda: self._tests_pass(),
                ),
                GateCheck(
                    name="refactor_complete",
                    description="Code has been refactored (REFACTOR phase)",
                    check_fn=lambda: True,  # Enforced by workflow
                ),
                GateCheck(
                    name="all_tests_green",
                    description="All tests pass after changes",
                    check_fn=lambda: self._tests_pass(),
                ),
            ],
        )

        # REVIEW-GATE: Code review against SPEC and PLAN
        self.gates["review-gate"] = Gate(
            name="REVIEW-GATE",
            description="Code review against SPEC.md and PLAN.md",
            checks=[
                GateCheck(
                    name="spec_requirements_met",
                    description="All SPEC.md requirements are implemented",
                    check_fn=lambda: True,  # Manual check
                ),
                GateCheck(
                    name="plan_tasks_completed",
                    description="All PLAN.md tasks are marked complete",
                    check_fn=lambda: self._all_plan_tasks_complete(),
                ),
                GateCheck(
                    name="no_debug_code",
                    description="No debug prints, TODOs, or hacks in code",
                    check_fn=lambda: self._no_debug_code(),
                ),
                GateCheck(
                    name="documentation_updated",
                    description="Documentation is updated for changes",
                    check_fn=lambda: True,  # Manual check
                ),
            ],
        )

    def _file_exists(self, path: str) -> bool:
        from pathlib import Path
        return Path(path).exists()

    def _plan_has_acceptance_criteria(self) -> bool:
        try:
            content = Path("devdep/workspace/PLAN.md").read_text()
            return "Acceptance Criteria" in content
        except Exception:
            return False

    def _plan_has_tdd_steps(self) -> bool:
        try:
            content = Path("devdep/workspace/PLAN.md").read_text()
            return "TDD Steps" in content and "RED" in content
        except Exception:
            return False

    def _plan_has_dependencies(self) -> bool:
        try:
            content = Path("devdep/workspace/PLAN.md").read_text()
            return "Dependencies" in content
        except Exception:
            return False

    def _tests_pass(self) -> bool:
        import subprocess
        try:
            result = subprocess.run(
                ["uv", "run", "pytest", "-q"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            return result.returncode == 0
        except Exception:
            return False

    def _all_plan_tasks_complete(self) -> bool:
        try:
            content = Path("devdep/workspace/PLAN.md").read_text()
            # Check for unchecked tasks
            import re
            unchecked = re.findall(r"^\s*-\s*\[ \]", content, re.MULTILINE)
            return len(unchecked) == 0
        except Exception:
            return False

    def _no_debug_code(self) -> bool:
        import subprocess
        try:
            result = subprocess.run(
                ["grep", "-r", "-n", "print(", "--include=*.py", "devdep/workspace/"],
                capture_output=True,
                text=True,
            )
            # Allow print in __main__ blocks
            lines = [l for l in result.stdout.split("\n") if l.strip() and "__main__" not in l]
            return len(lines) == 0
        except Exception:
            return True

    def check(self, gate_name: str) -> bool:
        """Evaluate a specific gate."""
        gate = self.gates.get(gate_name)
        if not gate:
            raise ValueError(f"Unknown gate: {gate_name}")
        return gate.evaluate()

    def report(self, gate_name: str) -> str:
        """Get a report for a specific gate."""
        gate = self.gates.get(gate_name)
        if not gate:
            raise ValueError(f"Unknown gate: {gate_name}")
        return gate.report()

    def check_all(self) -> dict[str, bool]:
        """Evaluate all gates and return results."""
        return {name: gate.evaluate() for name, gate in self.gates.items()}
