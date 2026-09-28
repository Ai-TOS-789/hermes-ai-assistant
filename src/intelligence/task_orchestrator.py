"""Task Orchestrator — plans and executes multi-step tasks."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Callable


class TaskStatus(Enum):
    PENDING = "pending"
    PLANNING = "planning"
    RUNNING = "running"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TaskStep:
    step_id: str
    description: str
    action_type: str  # 'search', 'code', 'shell', 'skill', 'chat'
    action_params: dict = field(default_factory=dict)
    depends_on: list[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[str] = None
    error: Optional[str] = None


@dataclass
class TaskPlan:
    task_id: str
    user_request: str
    steps: list[TaskStep] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    created_at: float = field(default_factory=float)
    completed_at: Optional[float] = None


class TaskOrchestrator:
    """Orchestrates multi-step tasks with dependency resolution and execution."""

    def __init__(self):
        self._tasks: dict[str, TaskPlan] = {}
        self._executors: dict[str, Callable] = {}

    def register_executor(self, action_type: str, executor: Callable) -> None:
        """Register an executor function for an action type."""
        self._executors[action_type] = executor

    def create_task(self, user_request: str, steps: list[dict]) -> TaskPlan:
        """Create a task plan from user request and step definitions."""
        task_id = str(uuid.uuid4())[:8]
        task_steps = [
            TaskStep(
                step_id=s.get("step_id", str(i)),
                description=s.get("description", ""),
                action_type=s.get("action_type", "chat"),
                action_params=s.get("params", {}),
                depends_on=s.get("depends_on", []),
            )
            for i, s in enumerate(steps)
        ]

        plan = TaskPlan(
            task_id=task_id,
            user_request=user_request,
            steps=task_steps,
        )
        self._tasks[task_id] = plan
        return plan

    def execute_task(self, task_id: str) -> dict:
        """Execute a task plan with dependency resolution."""
        plan = self._tasks.get(task_id)
        if not plan:
            return {"error": f"Task {task_id} not found"}

        plan.status = TaskStatus.RUNNING
        results = {}

        # Topological sort for dependency resolution
        executed = set()
        while len(executed) < len(plan.steps):
            ready = [s for s in plan.steps if s.step_id not in executed and all(d in executed for d in s.depends_on)]

            if not ready:
                # Circular dependency or missing dependency
                pending = [s.step_id for s in plan.steps if s.step_id not in executed]
                plan.status = TaskStatus.FAILED
                return {"error": f"Circular/missing dependency: {pending}"}

            for step in ready:
                result = self._execute_step(step)
                results[step.step_id] = result
                executed.add(step.step_id)

        plan.status = TaskStatus.COMPLETED
        plan.completed_at = __import__('time').time()
        return {"task_id": task_id, "results": results, "status": "completed"}

    def _execute_step(self, step: TaskStep) -> Optional[str]:
        """Execute a single task step."""
        executor = self._executors.get(step.action_type)
        if not executor:
            step.error = f"No executor for action type: {step.action_type}"
            step.status = TaskStatus.FAILED
            return None

        try:
            step.status = TaskStatus.RUNNING
            result = executor(**step.action_params)
            step.status = TaskStatus.COMPLETED
            step.result = str(result)[:500]
            return step.result
        except Exception as e:
            step.status = TaskStatus.FAILED
            step.error = str(e)
            return None

    def get_task(self, task_id: str) -> Optional[TaskPlan]:
        return self._tasks.get(task_id)
