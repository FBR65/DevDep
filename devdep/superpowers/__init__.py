"""
Superpowers - Structured AI Development Methodology

A skill-driven, TDD-enforced development system for AI-assisted coding.
Based on https://github.com/obra/superpowers
"""

__version__ = "1.0.0"

from .session import SuperpowersSession
from .skills import SkillRegistry
from .gates import GateKeeper

__all__ = ["SuperpowersSession", "SkillRegistry", "GateKeeper"]
