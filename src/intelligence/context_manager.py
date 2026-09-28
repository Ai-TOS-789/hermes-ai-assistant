"""Context Manager — smart context accumulation and retrieval for conversations."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ContextFrame:
    timestamp: float
    role: str  # 'user' | 'assistant' | 'system'
    content: str
    intent: Optional[str] = None
    tokens: int = 0
    metadata: dict = field(default_factory=dict)


@dataclass
class SessionContext:
    session_id: str
    frames: list[ContextFrame] = field(default_factory=list)
    summary: str = ""
    total_tokens: int = 0
    created_at: float = field(default_factory=time.time)
    last_active: float = field(default_factory=time.time)


class ContextManager:
    """Manages conversation context with intelligent summarization and retrieval."""

    def __init__(self, max_frames: int = 50, max_tokens: int = 16000):
        self.max_frames = max_frames
        self.max_tokens = max_tokens
        self._sessions: dict[str, SessionContext] = {}

    def create_session(self, session_id: str) -> SessionContext:
        ctx = SessionContext(session_id=session_id)
        self._sessions[session_id] = ctx
        return ctx

    def get_session(self, session_id: str) -> Optional[SessionContext]:
        ctx = self._sessions.get(session_id)
        if ctx:
            ctx.last_active = time.time()
        return ctx

    def add_message(self, session_id: str, role: str, content: str, intent: Optional[str] = None) -> None:
        ctx = self._sessions.get(session_id)
        if not ctx:
            ctx = self.create_session(session_id)

        frame = ContextFrame(
            timestamp=time.time(),
            role=role,
            content=content,
            intent=intent,
            tokens=len(content.split()),
        )
        ctx.frames.append(frame)
        ctx.total_tokens += frame.tokens
        ctx.last_active = time.time()

        # Trim if over limit
        while ctx.total_tokens > self.max_tokens and len(ctx.frames) > 2:
            removed = ctx.frames.pop(0)
            ctx.total_tokens -= removed.tokens

        while len(ctx.frames) > self.max_frames:
            removed = ctx.frames.pop(0)
            ctx.total_tokens -= removed.tokens

    def get_relevant_context(self, session_id: str, query: str, max_frames: int = 10) -> list[ContextFrame]:
        """Retrieve context frames relevant to a query using keyword matching."""
        ctx = self._sessions.get(session_id)
        if not ctx:
            return []

        query_words = set(query.lower().split())
        scored = []

        for frame in ctx.frames:
            content_words = set(frame.content.lower().split())
            overlap = len(query_words & content_words)
            if overlap > 0:
                scored.append((overlap, frame))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [f for _, f in scored[:max_frames]]

    def summarize_session(self, session_id: str) -> str:
        """Generate a summary of the session for context compression."""
        ctx = self._sessions.get(session_id)
        if not ctx or not ctx.frames:
            return ""

        # Simple extractive summary: first and last user messages + key intents
        user_msgs = [f.content for f in ctx.frames if f.role == 'user']
        intents = set(f.intent for f in ctx.frames if f.intent)

        summary_parts = []
        if user_msgs:
            summary_parts.append(f"First query: {user_msgs[0][:100]}")
            summary_parts.append(f"Last query: {user_msgs[-1][:100]}")
        if intents:
            summary_parts.append(f"Intents: {', '.join(intents)}")

        return " | ".join(summary_parts)

    def get_stats(self, session_id: str) -> dict:
        ctx = self._sessions.get(session_id)
        if not ctx:
            return {}
        return {
            "session_id": session_id,
            "frame_count": len(ctx.frames),
            "total_tokens": ctx.total_tokens,
            "created_at": ctx.created_at,
            "last_active": ctx.last_active,
            "summary": ctx.summary,
        }
