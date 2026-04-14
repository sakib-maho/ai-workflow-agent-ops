# AI Workflow Agent Ops

Backend project for AI-assisted workflow operations with approval gates, execution tracking, and retry handling.

## Current Capabilities

- create workflows with mixed agent and approval steps
- start workflow execution until approval gates
- approve or reject waiting workflows via decision endpoint
- inspect workflow and step state through list/detail APIs

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
uvicorn agent_ops.main:app --reload
```

Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

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

## License

MIT License.
