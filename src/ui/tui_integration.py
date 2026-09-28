"""TUI Integration Layer — bridges AI Assistant with Hermes TUI."""
from __future__ import annotations

from typing import Optional


class TUIIntegration:
    """Bridges AI Assistant with Hermes TUI."""

    def __init__(self, assistant: 'AIAssistant'):
        self.assistant = assistant
        self._status_hooks = []

    def register_status_hook(self, hook):
        """Register a hook for status updates."""
        self._status_hooks.append(hook)

    def _emit_status(self, status: str, data: dict = None):
        """Emit status update to hooks."""
        for hook in self._status_hooks:
            try:
                hook(status, data or {})
            except Exception:
                pass

    def process_input(self, user_input: str, session_id: str = "default") -> dict:
        """Process input through AI and return TUI-compatible response."""
        self._emit_status("processing", {"input": user_input[:50]})

        result = self.assistant.process(user_input, session_id)

        self._emit_status("complete", result)

        return self._format_for_tui(result)

    def _format_for_tui(self, result: dict) -> dict:
        """Format AI response for TUI display."""
        return {
            "intent": result["intent"],
            "confidence": result["confidence"],
            "skill": result["skill"],
            "output": result["response"].get("output", ""),
            "type": result["response"].get("type", "chat"),
            "memories": result.get("memories", []),
            "session": result.get("session_stats", {}),
        }

    def get_overlay_data(self) -> dict:
        """Get data for TUI overlay display."""
        status = self.assistant.get_status()
        return {
            "mode": "AI Assistant",
            "intent": status,
            "memories_count": status.get("memory", {}).get("entries", 0),
            "skills_count": status.get("skills", 0),
            "agents_active": status.get("agents", {}).get("active_agents", 0),
        }
