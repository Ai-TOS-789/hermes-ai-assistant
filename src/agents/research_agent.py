"""AI Research Agent — web research and knowledge gathering."""
from __future__ import annotations

from typing import Optional


class ResearchAgent:
    """Agent specialized in research tasks."""

    def __init__(self, web_search_fn=None):
        self._search = web_search_fn or self._default_search

    def research(self, query: str, depth: int = 2) -> dict:
        """Perform research on a topic."""
        results = {
            "query": query,
            "depth": depth,
            "sources": [],
            "summary": "",
            "key_findings": [],
        }

        # Simulate research with multiple search rounds
        for i in range(depth):
            search_results = self._search(query, limit=3)
            results["sources"].extend(search_results.get("data", {}).get("web", []))

        # Generate summary from sources
        if results["sources"]:
            results["summary"] = f"Research on '{query}': found {len(results['sources'])} sources."
            results["key_findings"] = [
                s.get("title", "") for s in results["sources"][:3]
            ]

        return results

    def compare(self, topic_a: str, topic_b: str) -> dict:
        """Compare two topics."""
        return {
            "comparison": f"{topic_a} vs {topic_b}",
            "topic_a_sources": [],
            "topic_b_sources": [],
            "differences": [],
        }

    def synthesize(self, queries: list[str]) -> dict:
        """Synthesize research from multiple queries."""
        return {
            "queries": queries,
            "synthesis": "Multi-query research synthesis",
        }

    def _default_search(self, query: str, limit: int = 5) -> dict:
        """Default search fallback."""
        return {"data": {"web": []}}
