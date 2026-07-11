from fastapi.testclient import TestClient

from omlx.server import app

client = TestClient(app)


def test_delete_session():
    session_id = "test-session-123"
    create_response = client.post(
        "/v1/sessions",
        json={"session_id": session_id},
        headers={"Authorization": "Bearer omlx-admin"},
    )
    assert create_response.status_code == 200

    response = client.delete(
        f"/v1/sessions/{session_id}",
        headers={"Authorization": "Bearer omlx-admin"},
    )

    assert response.status_code == 200
    assert response.json()["success"] is True

    get_response = client.get(
        f"/v1/sessions/{session_id}",
        headers={"Authorization": "Bearer omlx-admin"},
    )
    assert get_response.status_code == 404
