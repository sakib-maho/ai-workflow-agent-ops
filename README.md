# AI Workflow Agent Ops

<!-- BrandCloud:readme-standard -->
[![Maintained](https://img.shields.io/badge/Maintained-yes-brightgreen.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/sakib-maho/ai-workflow-agent-ops/actions/workflows/ci.yml/badge.svg)](https://github.com/sakib-maho/ai-workflow-agent-ops/actions/workflows/ci.yml)

Backend project for AI-assisted workflow operations with approval gates, execution tracking, and retry handling.

## Current Capabilities

- create workflows with mixed agent and approval steps
- start workflow execution until approval gates
- approve or reject waiting workflows via decision endpoint
- track failed steps with error context and retry them
- inspect workflow and step state through list/detail APIs

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
uvicorn agent_ops.main:app --reload
```

Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Docker

```bash
docker build -t ai-workflow-agent-ops .
docker run --rm -p 8000:8000 ai-workflow-agent-ops
```

## API Flow Example

Create workflow:

```bash
curl -X POST "http://127.0.0.1:8000/v1/workflows" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Support ticket escalation",
    "requester": "ops-bot",
    "steps": [
      {"name": "Classify ticket", "step_type": "agent", "instructions": "Label ticket severity"},
      {"name": "Supervisor review", "step_type": "approval", "instructions": "Approve escalation"},
      {"name": "Notify on-call", "step_type": "agent", "instructions": "Send pager alert"}
    ]
  }'
```

Start workflow:

```bash
curl -X POST "http://127.0.0.1:8000/v1/workflows/{workflow_id}/start"
```

Retry failed workflow step:

```bash
curl -X POST "http://127.0.0.1:8000/v1/workflows/{workflow_id}/retry"
```

## Quality Checks

```bash
pytest -q
python scripts/run_scenarios.py
```

## Architecture (Current)

- **Orchestrator:** in-memory workflow state machine
- **Step Types:** `agent` and `approval`
- **Resilience:** transient failure simulation + retry endpoint
- **Governance:** explicit approve/reject decision API
- **Ops Quality:** test suite + scenario runner + CI workflow

## License

MIT License.
