"""
Skill loading, discovery, and invocation for the Superpowers system.

Implements the 1% Rule: if there's even a 1% chance a skill applies, it MUST be invoked.
"""

import os
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Skill:
    """Represents a loaded skill with its metadata and content."""
    slug: str
    name: str
    version: str
    description: str
    triggers: list[str] = field(default_factory=list)
    content: str = ""
    filepath: Optional[Path] = None

    def applies_to(self, context: str) -> bool:
        """
        Check if this skill applies to the given context.
        Implements the 1% Rule: if ANY trigger or keyword matches, return True.
        This is intentionally permissive — even a 1% chance means invoke.
        """
        import re

        def extract_words(text: str) -> set[str]:
            """Extract all meaningful words from text, including splitting hyphens."""
            text = text.lower()
            # Split on non-alphanumeric, including hyphens and underscores
            words = re.findall(r'[a-z]{3,}', text)
            return set(words)

        context_words = extract_words(context)
        if not context_words:
            return False

        # Check triggers
        for trigger in self.triggers:
            trigger_words = extract_words(trigger)
            if trigger_words & context_words:  # Any common word
                return True
            # Also check substring in either direction
            trigger_lower = trigger.lower()
            if any(tw in context.lower() for tw in trigger_words):
                return True

        # Check skill name
        name_words = extract_words(self.name)
        if name_words & context_words:
            return True
        name_lower = self.name.lower()
        if any(nw in context.lower() for nw in name_words):
            return True
        if any(cw in name_lower for cw in context_words):
            return True

        # Check description
        desc_words = extract_words(self.description)
        if desc_words & context_words:
            return True
        desc_lower = self.description.lower()
        if any(dw in context.lower() for dw in desc_words):
            return True
        if any(cw in desc_lower for cw in context_words):
            return True

        # Check slug
        slug_words = extract_words(self.slug)
        if slug_words & context_words:
            return True
        slug_lower = self.slug.lower()
        if any(sw in context.lower() for sw in slug_words):
            return True
        if any(cw in slug_lower for cw in context_words):
            return True

        return False


class SkillRegistry:
    """Discovers and manages all available skills."""

    SKILL_DIR = Path(__file__).parent.parent / ".superpowers" / "skills"
    YAML_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)

    def __init__(self, skill_dir: Optional[Path] = None):
        self.skill_dir = skill_dir or self.SKILL_DIR
        self.skills: dict[str, Skill] = {}
        self._discover()

    def _parse_frontmatter(self, content: str) -> tuple[dict, str]:
        """Parse YAML frontmatter from markdown content."""
        match = self.YAML_PATTERN.match(content)
        if not match:
            return {}, content

        yaml_text, body = match.groups()
        metadata = {}
        for line in yaml_text.strip().split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()
                if value.startswith("[") and value.endswith("]"):
                    # Parse list
                    value = [v.strip().strip('"').strip("'") for v in value[1:-1].split(",")]
                metadata[key] = value
        return metadata, body

    def _discover(self) -> None:
        """Scan the skills directory and load all SKILL.md files."""
        if not self.skill_dir.exists():
            raise FileNotFoundError(f"Skill directory not found: {self.skill_dir}")

        for filepath in self.skill_dir.glob("*.md"):
            content = filepath.read_text(encoding="utf-8")
            metadata, body = self._parse_frontmatter(content)

            skill = Skill(
                slug=metadata.get("skill", filepath.stem),
                name=metadata.get("name", filepath.stem),
                version=metadata.get("version", "0.0.0"),
                description=metadata.get("description", ""),
                triggers=metadata.get("triggers", []),
                content=body,
                filepath=filepath,
            )
            self.skills[skill.slug] = skill

    def get(self, slug: str) -> Optional[Skill]:
        """Get a skill by its slug."""
        return self.skills.get(slug)

    def list_skills(self) -> list[Skill]:
        """List all discovered skills."""
        return list(self.skills.values())

    def check_1_percent_rule(self, context: str) -> list[Skill]:
        """
        Apply the 1% Rule: return ALL skills that could apply to the context.
        If there's even a 1% chance a skill applies, it MUST be returned.
        """
        applicable = []
        for skill in self.skills.values():
            if skill.applies_to(context):
                applicable.append(skill)
        return applicable

    def invoke(self, slug: str) -> str:
        """Invoke a skill by slug and return its content."""
        skill = self.get(slug)
        if not skill:
            raise ValueError(f"Skill not found: {slug}")
        return skill.content
