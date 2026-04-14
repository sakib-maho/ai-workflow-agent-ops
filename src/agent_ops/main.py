"""FastAPI entrypoint for AI Workflow Agent Ops."""

from fastapi import FastAPI, HTTPException

from .models import (
    DecisionRequest,
    WorkflowCreateRequest,
    WorkflowCreateResponse,
    WorkflowView,
)
from .workflow import WorkflowStore, to_view

app = FastAPI(
    title="AI Workflow Agent Ops",
    version="0.1.0",
    description="Workflow orchestration API scaffold for agent operations.",
)

workflow_store = WorkflowStore()


@app.get("/", tags=["meta"])
def root() -> dict[str, str]:
    return {"service": "ai-workflow-agent-ops", "status": "ok"}


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.post("/v1/workflows", response_model=WorkflowCreateResponse, tags=["workflow"])
def create_workflow(payload: WorkflowCreateRequest) -> WorkflowCreateResponse:
    workflow = workflow_store.create(payload)
    return WorkflowCreateResponse(workflow_id=workflow.workflow_id, status=workflow.status)


@app.get("/v1/workflows", response_model=list[WorkflowView], tags=["workflow"])
def list_workflows() -> list[WorkflowView]:
    return [to_view(item) for item in workflow_store.list_all()]


@app.get("/v1/workflows/{workflow_id}", response_model=WorkflowView, tags=["workflow"])
def get_workflow(workflow_id: str) -> WorkflowView:
    try:
        workflow = workflow_store.get(workflow_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return to_view(workflow)


@app.post("/v1/workflows/{workflow_id}/start", response_model=WorkflowView, tags=["workflow"])
def start_workflow(workflow_id: str) -> WorkflowView:
    try:
        workflow = workflow_store.start(workflow_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return to_view(workflow)


@app.post(
    "/v1/workflows/{workflow_id}/decision",
    response_model=WorkflowView,
    tags=["workflow"],
)
def workflow_decision(workflow_id: str, payload: DecisionRequest) -> WorkflowView:
    try:
        workflow = workflow_store.decide(workflow_id, approved=payload.approved)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    return to_view(workflow)


@app.post("/v1/workflows/{workflow_id}/retry", response_model=WorkflowView, tags=["workflow"])
def retry_workflow(workflow_id: str) -> WorkflowView:
    try:
        workflow = workflow_store.retry(workflow_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    return to_view(workflow)
