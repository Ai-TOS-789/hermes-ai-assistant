"""Tests for Hermes AI Assistant."""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from intelligence.intent_analyzer import IntentAnalyzer, IntentType
from intelligence.context_manager import ContextManager, SessionContext
from intelligence.task_orchestrator import TaskOrchestrator, TaskStatus
from intelligence.skill_router import SkillRouter
from agents.multi_agent import MultiAgentOrchestrator, AgentRole
from agents.research_agent import ResearchAgent
from agents.code_agent import CodeAgent
from memory.memory_manager import MemoryManager
from integrations.hub import WebSearch, ToolExecutor, IntegrationHub
from core.assistant import AIAssistant
from ui.tui_integration import TUIIntegration


class TestIntentAnalyzer:
    def setup_method(self):
        self.analyzer = IntentAnalyzer()

    def test_search_intent(self):
        result = self.analyzer.analyze("ค้นหา Python tutorial")
        assert result.intent_type == IntentType.SEARCH
        assert result.confidence > 0

    def test_code_intent(self):
        result = self.analyzer.analyze("เขียนโค้ด Python")
        assert result.intent_type in (IntentType.CODE, IntentType.SEARCH)

    def test_shell_intent(self):
        result = self.analyzer.analyze("รัน ls -la")
        assert result.intent_type in (IntentType.SHELL, IntentType.SEARCH)

    def test_thai_text(self):
        result = self.analyzer.analyze("ช่วยวิจัยเรื่อง AI")
        assert result.confidence > 0
        assert result.requires_web is True


class TestContextManager:
    def setup_method(self):
        self.cm = ContextManager()

    def test_session_lifecycle(self):
        ctx = self.cm.create_session("test1")
        assert ctx.session_id == "test1"

        self.cm.add_message("test1", "user", "Hello")
        self.cm.add_message("test1", "assistant", "Hi there")

        stats = self.cm.get_stats("test1")
        assert stats["frame_count"] == 2

    def test_context_retrieval(self):
        self.cm.add_message("test2", "user", "Python programming")
        self.cm.add_message("test2", "user", "JavaScript basics")

        relevant = self.cm.get_relevant_context("test2", "Python")
        assert len(relevant) > 0


class TestTaskOrchestrator:
    def setup_method(self):
        self.to = TaskOrchestrator()

    def test_task_creation(self):
        plan = self.to.create_task("Test task", [
            {"description": "Step 1", "action_type": "chat"},
        ])
        assert plan.task_id is not None
        assert len(plan.steps) == 1

    def test_executor_registration(self):
        def my_executor(**kwargs):
            return "done"

        self.to.register_executor("custom", my_executor)
        plan = self.to.create_task("Test", [
            {"description": "Custom step", "action_type": "custom"},
        ])
        result = self.to.execute_task(plan.task_id)
        assert result["status"] == "completed"


class TestSkillRouter:
    def setup_method(self):
        self.router = SkillRouter()

    def test_skill_discovery(self):
        skills = self.router.discover_skills()
        assert len(skills) > 0

    def test_skill_matching(self):
        skill = self.router.find_skill("ค้นหาอะไรบางอย่าง")
        assert skill is not None

    def test_skill_not_matched(self):
        skill = self.router.find_skill("xyz123random")
        # May or may not match depending on keywords


class TestMultiAgentOrchestrator:
    def setup_method(self):
        self.mao = MultiAgentOrchestrator()

    def test_agent_registration(self):
        def handler(desc, payload):
            return "result"

        self.mao.register_agent(AgentRole.RESEARCHER, handler)
        assert self.mao.get_status()["active_agents"] == 1

    def test_delegation(self):
        def handler(desc, payload):
            return f"Handled: {desc}"

        self.mao.register_agent(AgentRole.CODER, handler)
        results = self.mao.delegate([
            {"role": "coder", "description": "Write a function"},
        ])
        assert len(results) == 1
        assert results[0].success is True


class TestMemoryManager:
    def setup_method(self):
        import tempfile
        self.mm = MemoryManager(memory_file=tempfile.mktemp(suffix=".json"))

    def test_store_recall(self):
        self.mm.store("key1", "value1", category="test")
        entry = self.mm.recall("key1")
        assert entry is not None
        assert entry.value == "value1"

    def test_search(self):
        self.mm.store("python", "Python programming", category="code")
        self.mm.store("javascript", "JS programming", category="code")

        results = self.mm.search("python")
        assert len(results) >= 1

    def test_learn(self):
        self.mm.learn({"intent": "search", "input": "test query"})
        stats = self.mm.get_stats()
        assert stats["entries"] > 0


class TestIntegrationHub:
    def setup_method(self):
        self.hub = IntegrationHub()

    def test_tool_registration(self):
        def my_tool():
            return "result"

        self.hub.tools.register("mytool", my_tool)
        assert "mytool" in self.hub.tools.list_tools()

    def test_tool_execution(self):
        self.hub.tools.register("add", lambda a, b: a + b)
        result = self.hub.tools.execute("add", a=2, b=3)
        assert result["success"] is True


class TestAIAssistant:
    def setup_method(self):
        self.assistant = AIAssistant()

    def test_process_chat(self):
        result = self.assistant.process("Hello", "test_session")
        assert "intent" in result
        assert "response" in result
        assert result["intent"] in ["chat", "question"]

    def test_process_search(self):
        result = self.assistant.process("ค้นหา Python", "test_session")
        assert result["intent"] == "search"

    def test_status(self):
        status = self.assistant.get_status()
        assert "intent_analyzer" in status
        assert "agents" in status
        assert "memory" in status

    def test_memory_learning(self):
        self.assistant.process("ค้นหา อาหาร", "learn_session")
        self.assistant.process("เขียน โค้ด", "learn_session")

        stats = self.assistant.memory.get_stats()
        assert stats["entries"] >= 2


class TestTUIIntegration:
    def setup_method(self):
        self.assistant = AIAssistant()
        self.tui = TUIIntegration(self.assistant)

    def test_process_input(self):
        result = self.tui.process_input("Hello", "test")
        assert "intent" in result
        assert "output" in result

    def test_overlay_data(self):
        data = self.tui.get_overlay_data()
        assert data["mode"] == "AI Assistant"
        assert "memories_count" in data
