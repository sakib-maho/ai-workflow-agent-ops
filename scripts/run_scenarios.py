"""Run deterministic workflow scenarios for quick verification."""

from fastapi.testclient import TestClient

from agent_ops.main import app, workflow_store


def scenario_happy_path(client: TestClient) -> None:
    create = client.post(
        "/v1/workflows",
        json={
            "title": "Happy path approval",
            "requester": "ops-bot",
            "steps": [
                {"name": "Classify", "step_type": "agent", "instructions": "Classify ticket"},
                {"name": "Approval", "step_type": "approval", "instructions": "Approve run"},
                {"name": "Notify", "step_type": "agent", "instructions": "Send update"},
            ],
        },
    )
    workflow_id = create.json()["workflow_id"]
    start = client.post(f"/v1/workflows/{workflow_id}/start")
    decision = client.post(
        f"/v1/workflows/{workflow_id}/decision",
        json={"approved": True, "reviewer": "lead", "note": "approved"},
    )
    print(
        f"[happy_path] start={start.json()['status']} final={decision.json()['status']} workflow={workflow_id}"
    )


def scenario_fail_retry(client: TestClient) -> None:
    create = client.post(
        "/v1/workflows",
        json={
            "title": "Fail then retry",
            "requester": "ops-bot",
            "steps": [
                {
                    "name": "Enrich",
                    "step_type": "agent",
                    "instructions": "FAIL_ONCE enrich context",
                },
                {"name": "Approval", "step_type": "approval", "instructions": "Approve"},
            ],
        },
    )
    workflow_id = create.json()["workflow_id"]
    first = client.post(f"/v1/workflows/{workflow_id}/start")
    retry = client.post(f"/v1/workflows/{workflow_id}/retry")
    print(
        f"[fail_retry] first={first.json()['status']} retry={retry.json()['status']} workflow={workflow_id}"
    )


def main() -> int:
    workflow_store.clear()
    client = TestClient(app)
    scenario_happy_path(client)
    scenario_fail_retry(client)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
