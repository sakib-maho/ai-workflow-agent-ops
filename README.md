# AI Workflow Agent Ops

Backend project for AI-assisted workflow operations with approval gates, execution tracking, and retry handling.

## Phase

This is the initial scaffold commit. Next commits will add:

- workflow creation and step execution simulation
- approval queue and decision endpoints
- retry logic with failure tracking
- tests, CI, and Docker runtime

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
uvicorn agent_ops.main:app --reload
```

Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## License

MIT License.
