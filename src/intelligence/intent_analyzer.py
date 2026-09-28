"""AI Intent Analyzer — classifies user intent and extracts entities."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class IntentType(Enum):
    SEARCH = "search"
    CODE = "code"
    FILE_OP = "file_operation"
    SHELL = "shell_command"
    SKILL = "skill_invoke"
    CHAT = "chat"
    TASK_PLAN = "task_plan"
    QUESTION = "question"
    RESEARCH = "research"
    UNKNOWN = "unknown"


@dataclass
class ExtractedEntity:
    type: str
    value: str
    confidence: float = 0.0


@dataclass
class Intent:
    intent_type: IntentType
    confidence: float
    entities: list[ExtractedEntity] = field(default_factory=list)
    raw_text: str = ""
    suggested_skill: Optional[str] = None
    requires_web: bool = False
    priority: int = 1  # 1=low, 5=critical


class IntentAnalyzer:
    """Analyzes user input to determine intent, extract entities, and route accordingly."""

    # Patterns for intent detection
    _PATTERNS: dict[IntentType, list[str]] = {
        IntentType.SEARCH: [r"(ค้นหา|search|หา|look up)\s+(.+)", r"(.+)\s+(คือ|what is|who is|how to)"],
        IntentType.CODE: [r"(เขียน|create|build|generate)\s+(.+code|script|program|function)", r"เขียนโค้ด", r"create.*file"],
        IntentType.FILE_OP: [r"(เปิด|edit|แก้|ดู|read|write|delete)\s+(ไฟล์|file|โปรแกรม)", r"(\S+\.\w+)"],
        IntentType.SHELL: [r"(รัน|run|execute|เช็ค|check|install|pip|npm|apt)", r"!(\w+)"],
        IntentType.SKILL: [r"/(\w+)", r"ใช้ skill (\w+)"],
        IntentType.RESEARCH: [r"(วิจัย|research|ศึกษา|compare|analyze|review)\s+(.+)", r"อธิบาย(.+)"],
        IntentType.TASK_PLAN: [r"(ทำแผน|plan|task|โต้ะทำงาน|จัดการ)", r"ช่วยฉัน(ทำ|จัด|วาง)"],
        IntentType.QUESTION: [r"(what|why|how|when|where|who|อะไร|ทำไม|อย่างไร|เมื่อไหร่|ที่ไหน|ใคร)"],
    }

    def analyze(self, text: str) -> Intent:
        text_lower = text.lower().strip()
        best_intent = IntentType.UNKNOWN
        best_confidence = 0.0
        best_entities: list[ExtractedEntity] = []

        for intent_type, patterns in self._PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, text_lower, re.IGNORECASE)
                if match:
                    confidence = 0.7 if intent_type != IntentType.UNKNOWN else 0.3
                    entities = self._extract_entities(intent_type, match, text)
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_intent = intent_type
                        best_entities = entities

        # Thai language bonus
        if any('\u0e00' <= c <= '\u0e7f' for c in text):
            best_confidence = min(1.0, best_confidence + 0.1)

        suggested_skill = self._match_skill(text_lower)
        requires_web = best_intent in (IntentType.SEARCH, IntentType.RESEARCH, IntentType.QUESTION)

        return Intent(
            intent_type=best_intent,
            confidence=best_confidence,
            entities=best_entities,
            raw_text=text,
            suggested_skill=suggested_skill,
            requires_web=requires_web,
            priority=self._compute_priority(best_intent),
        )

    def _extract_entities(self, intent_type: IntentType, match: re.Match, raw: str) -> list[ExtractedEntity]:
        entities = []
        groups = match.groups()
        if groups:
            for g in groups:
                if g and len(g.strip()) > 1:
                    entities.append(ExtractedEntity(
                        type=intent_type.value,
                        value=g.strip()[:100],
                        confidence=0.8,
                    ))
        return entities

    def _match_skill(self, text: str) -> Optional[str]:
        skill_keywords = {
            "research": "arxiv",
            "search": "web_search",
            "code": "code_review",
            "file": "pdf",
            "image": "gif_search",
            "email": "email",
            "meeting": "meeting-action-items",
            "price": "product-price-monitor",
        }
        for kw, skill in skill_keywords.items():
            if kw in text:
                return skill
        return None

    def _compute_priority(self, intent: IntentType) -> int:
        high_priority = {IntentType.SHELL, IntentType.CODE, IntentType.FILE_OP}
        return 4 if intent in high_priority else 2
