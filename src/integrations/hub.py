"""Integrations — web search, tools, and external services."""
from __future__ import annotations

import json
from typing import Optional


class WebSearch:
    """Web search integration using Hermes web_search tool."""

    def __init__(self, search_fn=None):
        self._search = search_fn

    def search(self, query: str, limit: int = 5) -> list[dict]:
        """Search the web."""
        if self._search:
            result = self._search(query, limit=limit)
            return result.get("data", {}).get("web", [])
        return []

    def search_with_context(self, query: str, context: str = "", limit: int = 5) -> dict:
        """Search with additional context for better results."""
        enriched_query = f"{context} {query}".strip()
        results = self.search(enriched_query, limit=limit)

        return {
            "query": enriched_query,
            "results": results,
            "count": len(results),
        }


class ToolExecutor:
    """Executes Hermes tools programmatically."""

    def __init__(self):
        self._tools: dict[str, callable] = {}

    def register(self, name: str, func: callable) -> None:
        """Register a tool function."""
        self._tools[name] = func

    def execute(self, name: str, **kwargs) -> Optional[dict]:
        """Execute a registered tool."""
        tool = self._tools.get(name)
        if not tool:
            return {"error": f"Tool '{name}' not registered"}

        try:
            result = tool(**kwargs)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_tools(self) -> list[str]:
        """List registered tools."""
        return list(self._tools.keys())


class IntegrationHub:
    """Central hub for all integrations."""

    def __init__(self):
        self.web_search = WebSearch()
        self.tools = ToolExecutor()
        self._hooks: dict[str, list[callable]] = {}

    def register_hook(self, event: str, hook: callable) -> None:
        """Register a hook for an event."""
        self._hooks.setdefault(event, []).append(hook)

    def emit(self, event: str, *args, **kwargs) -> None:
        """Emit an event to all registered hooks."""
        for hook in self._hooks.get(event, []):
            try:
                hook(*args, **kwargs)
            except Exception:
                pass

    def health_check(self) -> dict:
        """Check integration health."""
        return {
            "web_search": self._check_web_search(),
            "tools": len(self.tools._tools),
            "hooks": {k: len(v) for k, v in self._hooks.items()},
        }

    def _check_web_search(self) -> str:
        if self.web_search._search:
            return "connected"
        return "disconnected"
