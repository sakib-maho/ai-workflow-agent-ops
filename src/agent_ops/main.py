"""FastAPI entrypoint for AI Workflow Agent Ops."""

from fastapi import FastAPI

app = FastAPI(
    title="AI Workflow Agent Ops",
    version="0.1.0",
    description="Workflow orchestration API scaffold for agent operations.",
)


@app.get("/", tags=["meta"])
def root() -> dict[str, str]:
    return {"service": "ai-workflow-agent-ops", "status": "ok"}


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "healthy"}
