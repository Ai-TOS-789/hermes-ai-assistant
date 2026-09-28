"""Multi-Agent Orchestrator — coordinates parallel agent execution."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Callable, Any


class AgentRole(Enum):
    RESEARCHER = "researcher"
    CODER = "coder"
    REVIEWER = "reviewer"
    TESTER = "tester"
    PLANNER = "planner"
    ANALYST = "analyst"


@dataclass
class AgentTask:
    task_id: str
    role: AgentRole
    description: str
    payload: dict = field(default_factory=dict)
    status: str = "pending"
    result: Optional[Any] = None
    error: Optional[str] = None
    parent_id: Optional[str] = None
    sibling_ids: list[str] = field(default_factory=list)


@dataclass
class AgentResult:
    task_id: str
    role: AgentRole
    success: bool
    output: str
    metrics: dict = field(default_factory=dict)


class MultiAgentOrchestrator:
    """Orchestrates multiple agents working in parallel on subtasks."""

    def __init__(self):
        self._agents: dict[str, Callable] = {}
        self._tasks: dict[str, AgentTask] = {}
        self._max_parallel = 4

    def register_agent(self, role: AgentRole, handler: Callable) -> None:
        """Register an agent handler for a role."""
        self._agents[role.value] = handler

    def delegate(self, tasks: list[dict]) -> list[AgentResult]:
        """Delegate tasks to agents in parallel where possible."""
        # Create task objects
        agent_tasks = []
        for t in tasks:
            task = AgentTask(
                task_id=str(uuid.uuid4())[:8],
                role=AgentRole(t["role"]),
                description=t.get("description", ""),
                payload=t.get("payload", {}),
                parent_id=t.get("parent_id"),
            )
            self._tasks[task.task_id] = task
            agent_tasks.append(task)

        # Group by parent for sibling tracking
        by_parent: dict[str, list[AgentTask]] = {}
        for t in agent_tasks:
            pid = t.parent_id or "root"
            by_parent.setdefault(pid, []).append(t)

        # Execute in waves (parallel within wave, sequential across waves)
        results = []
        remaining = list(agent_tasks)

        while remaining:
            # Find tasks whose dependencies are met
            wave = [t for t in remaining if all(
                dep in {r.task_id for r in results} for dep in t.sibling_ids
            )]

            if not wave:
                # All remaining have unmet deps — break cycle
                for t in remaining:
                    t.status = "failed"
                    t.error = "Unmet dependency"
                    results.append(AgentResult(t.task_id, t.role, False, t.error))
                break

            # Execute wave (simulated parallel)
            for task in wave:
                handler = self._agents.get(task.role.value)
                if handler:
                    try:
                        task.status = "running"
                        output = handler(task.description, task.payload)
                        task.status = "completed"
                        task.result = output
                        results.append(AgentResult(
                            task.task_id, task.role, True,
                            str(output), {"duration": 0}
                        ))
                    except Exception as e:
                        task.status = "failed"
                        task.error = str(e)
                        results.append(AgentResult(
                            task.task_id, task.role, False, str(e)
                        ))
                else:
                    task.status = "failed"
                    task.error = f"No agent for role: {task.role}"
                    results.append(AgentResult(
                        task.task_id, task.role, False,
                        f"No agent registered for {task.role.value}"
                    ))

            remaining = [t for t in remaining if t not in wave]

        return results

    def get_status(self) -> dict:
        """Get orchestrator status summary."""
        from collections import Counter
        status_counts = Counter(t.status for t in self._tasks.values())
        role_counts = Counter(t.role.value for t in self._tasks.values())
        return {
            "total_tasks": len(self._tasks),
            "status": dict(status_counts),
            "by_role": dict(role_counts),
            "active_agents": len(self._agents),
        }
