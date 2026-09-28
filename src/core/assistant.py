"""Intelligent Assistant — main AI orchestrator."""
from __future__ import annotations

import time
from typing import Optional

from intelligence.intent_analyzer import IntentAnalyzer, Intent
from intelligence.context_manager import ContextManager, SessionContext
from intelligence.task_orchestrator import TaskOrchestrator, TaskPlan
from intelligence.skill_router import SkillRouter
from agents.multi_agent import MultiAgentOrchestrator, AgentRole
from agents.research_agent import ResearchAgent
from agents.code_agent import CodeAgent
from memory.memory_manager import MemoryManager
from integrations.hub import IntegrationHub


class AIAssistant:
    """The Intelligent Assistant — orchestrates all AI capabilities."""

    def __init__(self):
        # Core intelligence
        self.intent_analyzer = IntentAnalyzer()
        self.context_manager = ContextManager()
        self.task_orchestrator = TaskOrchestrator()
        self.skill_router = SkillRouter()

        # Agents
        self.agent_orchestrator = MultiAgentOrchestrator()
        self.research_agent = ResearchAgent()
        self.code_agent = CodeAgent()

        # Memory
        self.memory = MemoryManager()

        # Integrations
        self.integrations = IntegrationHub()

        # Register agents
        self.agent_orchestrator.register_agent(AgentRole.RESEARCHER, self._research_handler)
        self.agent_orchestrator.register_agent(AgentRole.CODER, self._code_handler)
        self.agent_orchestrator.register_agent(AgentRole.REVIEWER, self._review_handler)
        self.agent_orchestrator.register_agent(AgentRole.PLANNER, self._plan_handler)

        # Register task executors
        self.task_orchestrator.register_executor("search", self._task_search)
        self.task_orchestrator.register_executor("code", self._task_code)
        self.task_orchestrator.register_executor("skill", self._task_skill)
        self.task_orchestrator.register_executor("chat", self._task_chat)

    def process(self, user_input: str, session_id: str = "default") -> dict:
        """Process user input through the AI pipeline."""
        # Step 1: Analyze intent
        intent = self.intent_analyzer.analyze(user_input)

        # Step 2: Update context
        self.context_manager.add_message(session_id, "user", user_input, intent.intent_type.value)

        # Step 3: Retrieve relevant memory
        relevant_memories = self.memory.search(user_input)

        # Step 4: Find matching skill
        matched_skill = self.skill_router.find_skill(user_input, intent.intent_type.value)

        # Step 5: Route to appropriate handler
        response = self._route_intent(intent, user_input, session_id)

        # Step 6: Store in context
        self.context_manager.add_message(session_id, "assistant", response.get("output", ""))

        # Step 7: Learn from interaction
        self.memory.learn({
            "intent": intent.intent_type.value,
            "input": user_input,
            "skill_used": matched_skill.name if matched_skill else None,
            "timestamp": time.time(),
        })

        return {
            "intent": intent.intent_type.value,
            "confidence": intent.confidence,
            "skill": matched_skill.name if matched_skill else None,
            "response": response,
            "memories": [m.key for m in relevant_memories[:3]],
            "session_stats": self.context_manager.get_stats(session_id),
        }

    def _route_intent(self, intent: Intent, text: str, session_id: str) -> dict:
        """Route intent to appropriate handler."""
        intent_type = intent.intent_type

        if intent_type.value == "search":
            return self._handle_search(text)
        elif intent_type.value == "research":
            return self._handle_research(text)
        elif intent_type.value == "code":
            return self._handle_code(text)
        elif intent_type.value == "skill":
            return self._handle_skill(text)
        elif intent_type.value == "task_plan":
            return self._handle_task_plan(text)
        elif intent_type.value == "shell":
            return self._handle_shell(text)
        else:
            return self._handle_chat(text, intent)

    def _handle_search(self, query: str) -> dict:
        """Handle search queries."""
        results = self.integrations.web_search.search(query)
        return {
            "output": f"Search results for '{query}': {len(results)} found",
            "results": results,
            "type": "search",
        }

    def _handle_research(self, topic: str) -> dict:
        """Handle research requests."""
        result = self.research_agent.research(topic)
        return {
            "output": result["summary"],
            "research": result,
            "type": "research",
        }

    def _handle_code(self, description: str) -> dict:
        """Handle code generation requests."""
        code = self.code_agent.generate(description)
        review = self.code_agent.review(code)
        return {
            "output": f"Generated code ({review['lines']} lines, score: {review['score']})",
            "code": code,
            "review": review,
            "type": "code",
        }

    def _handle_skill(self, command: str) -> dict:
        """Handle skill invocations."""
        parts = command.strip("/").split()
        skill_name = parts[0] if parts else command
        skill = self.skill_router.find_skill(skill_name)

        if skill:
            prompt = self.skill_router.get_skill_prompt(skill_name)
            return {
                "output": f"Invoked skill: {skill_name}",
                "skill": skill.name,
                "prompt": prompt[:500],
                "type": "skill",
            }
        return {
            "output": f"Unknown skill: {skill_name}",
            "type": "skill",
        }

    def _handle_task_plan(self, request: str) -> dict:
        """Handle task planning requests."""
        # Parse steps from request (simple heuristic)
        steps = [{"description": request, "action_type": "chat"}]
        plan = self.task_orchestrator.create_task(request, steps)
        return {
            "output": f"Task plan created: {plan.task_id}",
            "plan": plan.task_id,
            "type": "task_plan",
        }

    def _handle_shell(self, command: str) -> dict:
        """Handle shell commands."""
        return {
            "output": f"Shell command queued: {command}",
            "type": "shell",
        }

    def _handle_chat(self, text: str, intent: Intent) -> dict:
        """Handle general chat."""
        context = self.context_manager.get_relevant_context("default", text)
        context_summary = "; ".join(f"{f.role}: {f.content[:50]}" for f in context[:3])

        return {
            "output": f"Assistant: Processing '{text[:50]}...' (intent: {intent.intent_type.value})",
            "context": context_summary,
            "type": "chat",
        }

    def _research_handler(self, desc: str, payload: dict) -> str:
        return f"Research complete: {desc}"

    def _code_handler(self, desc: str, payload: dict) -> str:
        return f"Code generated for: {desc}"

    def _review_handler(self, desc: str, payload: dict) -> str:
        return f"Review complete: {desc}"

    def _plan_handler(self, desc: str, payload: dict) -> str:
        return f"Plan created: {desc}"

    def _task_search(self, **kwargs) -> str:
        return self._handle_search(kwargs.get("query", ""))["output"]

    def _task_code(self, **kwargs) -> str:
        return self._handle_code(kwargs.get("description", ""))["output"]

    def _task_skill(self, **kwargs) -> str:
        return self._handle_skill(kwargs.get("command", ""))["output"]

    def _task_chat(self, **kwargs) -> str:
        return self._handle_chat(kwargs.get("text", ""), None)["output"]

    def get_status(self) -> dict:
        """Get assistant status."""
        return {
            "intent_analyzer": "ready",
            "context_manager": self.context_manager.get_stats("default"),
            "agents": self.agent_orchestrator.get_status(),
            "memory": self.memory.get_stats(),
            "integrations": self.integrations.health_check(),
            "skills": len(self.skill_router._skills),
        }
