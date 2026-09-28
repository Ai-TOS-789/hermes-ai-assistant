"""Skill Router — intelligent skill discovery and invocation."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SkillInfo:
    name: str
    description: str
    category: str = "general"
    triggers: list[str] = field(default_factory=list)
    path: Optional[str] = None


class SkillRouter:
    """Routes user intents to appropriate skills with fuzzy matching."""

    def __init__(self, skills_dir: Optional[str] = None):
        self._skills: dict[str, SkillInfo] = {}
        self._skills_dir = skills_dir or os.path.expanduser("~/.hermes/skills")
        self._load_builtin_skills()

    def _load_builtin_skills(self) -> None:
        """Load known Hermes skills catalog."""
        builtin = {
            "arxiv": SkillInfo("arxiv", "Search arXiv papers", "research", ["วิจัย", "paper", "academic"]),
            "web_search": SkillInfo("web_search", "Search the web", "research", ["ค้นหา", "search", "หา"]),
            "pdf": SkillInfo("pdf", "PDF manipulation", "productivity", ["pdf", "document"]),
            "xlsx": SkillInfo("xlsx", "Excel spreadsheet", "productivity", ["excel", "spreadsheet"]),
            "docx": SkillInfo("docx", "Word document", "productivity", ["word", "document"]),
            "powerpoint": SkillInfo("powerpoint", "Presentation", "productivity", ["ppt", "presentation"]),
            "gif_search": SkillInfo("gif_search", "Search GIFs", "media", ["gif", "image"]),
            "email": SkillInfo("email", "Email management", "email", ["email", "inbox"]),
            "meeting-action-items": SkillInfo("meeting-action-items", "Meeting notes to action items", "productivity", ["meeting", "action items"]),
            "product-price-monitor": SkillInfo("product-price-monitor", "Price monitoring", "productivity", ["price", "monitor"]),
            "code-review": SkillInfo("code-review", "Code review", "development", ["review", "code", "bug"]),
            "systematic-debugging": SkillInfo("systematic-debugging", "Debugging", "development", ["debug", "fix", "error"]),
            "test-driven-development": SkillInfo("test-driven-development", "TDD workflow", "development", ["test", "tdd"]),
            "map": SkillInfo("maps", "Geocoding and routes", "maps", ["map", "route", "geo"]),
        }
        self._skills = builtin

    def discover_skills(self, directory: Optional[str] = None) -> list[SkillInfo]:
        """Discover skills from a directory."""
        skills_dir = directory or self._skills_dir
        discovered = list(self._skills.values())

        if os.path.isdir(skills_dir):
            for entry in os.listdir(skills_dir):
                skill_path = os.path.join(skills_dir, entry)
                if os.path.isdir(skill_path):
                    skill_file = os.path.join(skill_path, "SKILL.md")
                    if os.path.exists(skill_file):
                        # Parse SKILL.md for metadata
                        info = self._parse_skill_md(skill_file, entry)
                        if info and info.name not in {s.name for s in discovered}:
                            discovered.append(info)

        return discovered

    def _parse_skill_md(self, path: str, name: str) -> Optional[SkillInfo]:
        """Parse SKILL.md frontmatter for skill info."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            desc = ""
            for line in content.split('\n'):
                if line.startswith('description:'):
                    desc = line.split(':', 1)[1].strip().strip('"\'')
                    break
            return SkillInfo(name=name, description=desc, category="custom")
        except Exception:
            return SkillInfo(name=name, description="Custom skill", category="custom")

    def find_skill(self, query: str, intent: Optional[str] = None) -> Optional[SkillInfo]:
        """Find the best matching skill for a query."""
        query_lower = query.lower()
        best_match = None
        best_score = 0

        for skill in self._skills.values():
            score = 0
            # Direct name match
            if skill.name.lower() in query_lower:
                score += 10
            # Trigger keyword match
            for trigger in skill.triggers:
                if trigger.lower() in query_lower:
                    score += 5
            # Category match
            if intent and skill.category == intent:
                score += 3
            # Description match
            if any(word in query_lower for word in skill.description.lower().split()):
                score += 1

            if score > best_score:
                best_score = score
                best_match = skill

        return best_match if best_score >= 3 else None

    def get_skill_prompt(self, skill_name: str) -> str:
        """Get the prompt/instruction for a skill."""
        skill_path = os.path.join(self._skills_dir, skill_name, "SKILL.md")
        if os.path.exists(skill_path):
            with open(skill_path, 'r', encoding='utf-8') as f:
                return f.read()
        return f"Skill: {skill_name} — no prompt file found."
