"""Pydantic models for workflow agent operations."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class WorkflowStatus(str, Enum):
    pending = "pending"
    waiting_approval = "waiting_approval"
    running = "running"
    completed = "completed"
    failed = "failed"
    rejected = "rejected"


class StepType(str, Enum):
    agent = "agent"
    approval = "approval"


class WorkflowStepInput(BaseModel):
    name: str = Field(..., min_length=2)
    step_type: StepType
    instructions: str = Field(..., min_length=4)


class WorkflowCreateRequest(BaseModel):
    title: str = Field(..., min_length=4)
    requester: str = Field(..., min_length=2)
    steps: list[WorkflowStepInput] = Field(..., min_length=1)


class WorkflowCreateResponse(BaseModel):
    workflow_id: str
    status: WorkflowStatus


class DecisionRequest(BaseModel):
    approved: bool
    reviewer: str = Field(..., min_length=2)
    note: str = Field(default="")


class WorkflowStepState(BaseModel):
    step_id: str
    name: str
    step_type: StepType
    instructions: str
    status: WorkflowStatus
    attempts: int = 0


class WorkflowView(BaseModel):
    workflow_id: str
    title: str
    requester: str
    status: WorkflowStatus
    created_at: datetime
    updated_at: datetime
    current_step_index: int
    steps: list[WorkflowStepState]
