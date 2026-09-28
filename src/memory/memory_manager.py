"""Memory Manager — persistent memory with learning capability."""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MemoryEntry:
    key: str
    value: str
    category: str = "general"
    timestamp: float = field(default_factory=time.time)
    access_count: int = 0
    metadata: dict = field(default_factory=dict)


class MemoryManager:
    """Persistent memory with learning and recall."""

    def __init__(self, memory_file: str = "~/.hermes/ai_assistant_memory.json"):
        self._file = os.path.expanduser(memory_file)
        self._memory: dict[str, MemoryEntry] = {}
        self._load()

    def store(self, key: str, value: str, category: str = "general", metadata: Optional[dict] = None) -> None:
        """Store a memory entry."""
        entry = MemoryEntry(
            key=key,
            value=value,
            category=category,
            metadata=metadata or {},
        )
        self._memory[key] = entry
        self._save()

    def recall(self, key: str) -> Optional[MemoryEntry]:
        """Recall a memory entry."""
        entry = self._memory.get(key)
        if entry:
            entry.access_count += 1
            entry.timestamp = time.time()
        return entry

    def search(self, query: str, category: Optional[str] = None) -> list[MemoryEntry]:
        """Search memory by keyword."""
        query_lower = query.lower()
        results = []

        for entry in self._memory.values():
            if category and entry.category != category:
                continue
            if (query_lower in entry.key.lower() or
                query_lower in entry.value.lower()):
                results.append(entry)

        # Sort by relevance (access count + recency)
        results.sort(key=lambda e: (e.access_count, e.timestamp), reverse=True)
        return results

    def learn(self, interaction: dict) -> None:
        """Learn from user interactions to improve future responses."""
        # Extract patterns from interactions
        if "intent" in interaction:
            key = f"intent_pattern:{interaction['intent']}"
            self.store(key, json.dumps(interaction), category="pattern")

        # Store preferences
        if "preference" in interaction:
            pref = interaction["preference"]
            self.store(f"preference:{pref.get('key', 'unknown')}",
                      json.dumps(pref), category="preference")

        self._save()

    def get_stats(self) -> dict:
        """Get memory statistics."""
        by_category: dict[str, int] = {}
        for entry in self._memory.values():
            by_category[entry.category] = by_category.get(entry.category, 0) + 1

        total_access = sum(e.access_count for e in self._memory.values())

        return {
            "entries": len(self._memory),
            "categories": by_category,
            "total_accesses": total_access,
            "file": self._file,
        }

    def _load(self) -> None:
        """Load memory from file."""
        if not os.path.exists(self._file):
            return
        try:
            with open(self._file, 'r') as f:
                data = json.load(f)
            for key, entry_data in data.items():
                self._memory[key] = MemoryEntry(**entry_data)
        except (json.JSONDecodeError, IOError):
            self._memory = {}

    def _save(self) -> None:
        """Save memory to file."""
        os.makedirs(os.path.dirname(self._file), exist_ok=True)
        data = {k: {"key": e.key, "value": e.value, "category": e.category,
                     "timestamp": e.timestamp, "access_count": e.access_count,
                     "metadata": e.metadata} for k, e in self._memory.items()}
        with open(self._file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
