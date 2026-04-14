from fastapi.testclient import TestClient

from agent_ops.main import app, workflow_store


client = TestClient(app)


def setup_function() -> None:
    workflow_store.clear()


def test_create_start_approve_workflow() -> None:
    create = client.post(
        "/v1/workflows",
        json={
            "title": "Ticket escalation",
            "requester": "ops-bot",
            "steps": [
                {"name": "Classify", "step_type": "agent", "instructions": "Classify severity"},
                {"name": "Approval", "step_type": "approval", "instructions": "Approve escalation"},
                {"name": "Notify", "step_type": "agent", "instructions": "Send notification"},
            ],
        },
    )
    assert create.status_code == 200
    workflow_id = create.json()["workflow_id"]

    start = client.post(f"/v1/workflows/{workflow_id}/start")
    assert start.status_code == 200
    assert start.json()["status"] == "waiting_approval"

    approve = client.post(
        f"/v1/workflows/{workflow_id}/decision",
        json={"approved": True, "reviewer": "team-lead", "note": "Proceed"},
    )
    assert approve.status_code == 200
    assert approve.json()["status"] == "completed"


def test_retry_after_fail_once_step() -> None:
    create = client.post(
        "/v1/workflows",
        json={
            "title": "Retry test workflow",
            "requester": "ops-bot",
            "steps": [
                {
                    "name": "Enrich data",
                    "step_type": "agent",
                    "instructions": "FAIL_ONCE enrich payload",
                },
                {"name": "Approval", "step_type": "approval", "instructions": "Approve"},
            ],
        },
    )
    workflow_id = create.json()["workflow_id"]

    start = client.post(f"/v1/workflows/{workflow_id}/start")
    assert start.status_code == 200
    assert start.json()["status"] == "failed"
    assert start.json()["steps"][0]["last_error"] != ""

    retry = client.post(f"/v1/workflows/{workflow_id}/retry")
    assert retry.status_code == 200
    assert retry.json()["status"] == "waiting_approval"
    assert retry.json()["steps"][0]["attempts"] == 2


def test_decision_conflict_when_not_waiting() -> None:
    create = client.post(
        "/v1/workflows",
        json={
            "title": "No approval gate",
            "requester": "ops-bot",
            "steps": [{"name": "Summarize", "step_type": "agent", "instructions": "Summarize"}],
        },
    )
    workflow_id = create.json()["workflow_id"]
    client.post(f"/v1/workflows/{workflow_id}/start")
    decision = client.post(
        f"/v1/workflows/{workflow_id}/decision",
        json={"approved": True, "reviewer": "lead", "note": ""},
    )
    assert decision.status_code == 409
