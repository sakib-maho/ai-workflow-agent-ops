"""In-memory workflow orchestration with approval gating."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List
from uuid import uuid4

from .models import (
    StepType,
    WorkflowCreateRequest,
    WorkflowStatus,
    WorkflowStepState,
    WorkflowStepInput,
    WorkflowView,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class StepRecord:
    step_id: str
    name: str
    step_type: StepType
    instructions: str
    status: WorkflowStatus = WorkflowStatus.pending
    attempts: int = 0


@dataclass(slots=True)
class WorkflowRecord:
    workflow_id: str
    title: str
    requester: str
    status: WorkflowStatus
    created_at: datetime
    updated_at: datetime
    current_step_index: int
    steps: List[StepRecord] = field(default_factory=list)


class WorkflowStore:
    """Store and process workflow records in memory."""

    def __init__(self) -> None:
        self._workflows: Dict[str, WorkflowRecord] = {}

    def create(self, payload: WorkflowCreateRequest) -> WorkflowRecord:
        workflow_id = f"wf-{uuid4().hex[:10]}"
        steps = [self._make_step(step) for step in payload.steps]
        now = utc_now()
        record = WorkflowRecord(
            workflow_id=workflow_id,
            title=payload.title,
            requester=payload.requester,
            status=WorkflowStatus.pending,
            created_at=now,
            updated_at=now,
            current_step_index=0,
            steps=steps,
        )
        self._workflows[workflow_id] = record
        return record

    def get(self, workflow_id: str) -> WorkflowRecord:
        if workflow_id not in self._workflows:
            raise KeyError(f"workflow not found: {workflow_id}")
        return self._workflows[workflow_id]

    def list_all(self) -> list[WorkflowRecord]:
        return sorted(
            self._workflows.values(),
            key=lambda item: item.created_at,
            reverse=True,
        )

    def start(self, workflow_id: str) -> WorkflowRecord:
        workflow = self.get(workflow_id)
        if workflow.status in {WorkflowStatus.completed, WorkflowStatus.rejected}:
            return workflow
        self._run_until_gate(workflow)
        return workflow

    def decide(self, workflow_id: str, approved: bool) -> WorkflowRecord:
        workflow = self.get(workflow_id)
        current = self._current_step(workflow)
        if current is None or current.step_type != StepType.approval:
            raise ValueError("workflow is not waiting on an approval step")
        if workflow.status != WorkflowStatus.waiting_approval:
            raise ValueError("workflow is not in waiting_approval state")

        if approved:
            current.status = WorkflowStatus.completed
            workflow.current_step_index += 1
            self._run_until_gate(workflow)
        else:
            current.status = WorkflowStatus.rejected
            workflow.status = WorkflowStatus.rejected
            workflow.updated_at = utc_now()
        return workflow

    def clear(self) -> None:
        self._workflows.clear()

    def _run_until_gate(self, workflow: WorkflowRecord) -> None:
        workflow.status = WorkflowStatus.running
        while workflow.current_step_index < len(workflow.steps):
            step = workflow.steps[workflow.current_step_index]
            if step.step_type == StepType.approval:
                step.status = WorkflowStatus.waiting_approval
                workflow.status = WorkflowStatus.waiting_approval
                workflow.updated_at = utc_now()
                return
            step.attempts += 1
            step.status = WorkflowStatus.completed
            workflow.current_step_index += 1

        workflow.status = WorkflowStatus.completed
        workflow.updated_at = utc_now()

    def _current_step(self, workflow: WorkflowRecord) -> StepRecord | None:
        if workflow.current_step_index >= len(workflow.steps):
            return None
        return workflow.steps[workflow.current_step_index]

    def _make_step(self, step: WorkflowStepInput) -> StepRecord:
        return StepRecord(
            step_id=f"step-{uuid4().hex[:8]}",
            name=step.name,
            step_type=step.step_type,
            instructions=step.instructions,
        )


def to_view(record: WorkflowRecord) -> WorkflowView:
    return WorkflowView(
        workflow_id=record.workflow_id,
        title=record.title,
        requester=record.requester,
        status=record.status,
        created_at=record.created_at,
        updated_at=record.updated_at,
        current_step_index=record.current_step_index,
        steps=[
            WorkflowStepState(
                step_id=step.step_id,
                name=step.name,
                step_type=step.step_type,
                instructions=step.instructions,
                status=step.status,
                attempts=step.attempts,
            )
            for step in record.steps
        ],
    )
