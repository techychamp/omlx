import pytest
from fastapi.testclient import TestClient
from omlx.server import app
import sqlite3
import os

client = TestClient(app)

def test_delete_session(monkeypatch):
    db_path = ":memory:"
    # Use monkeypatch to patch _get_db_path properly since it might be reloaded
    monkeypatch.setattr("omlx.server._get_db_path", lambda: db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables if they don't exist
    cursor.execute("CREATE TABLE IF NOT EXISTS sessions (id TEXT PRIMARY KEY)")
    cursor.execute("CREATE TABLE IF NOT EXISTS messages (id TEXT PRIMARY KEY, session_id TEXT)")

    # Insert test data
    cursor.execute("INSERT INTO sessions (id) VALUES ('test-session-123')")
    cursor.execute("INSERT INTO messages (id, session_id) VALUES ('msg-1', 'test-session-123')")
    conn.commit()
    conn.close()

    # Call endpoint
    response = client.delete("/v1/sessions/test-session-123", headers={"Authorization": "Bearer omlx-admin"})

    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "Session test-session-123 deleted."}

    # Verify deletion
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sessions WHERE id = 'test-session-123'")
    assert cursor.fetchone() is None
    cursor.execute("SELECT * FROM messages WHERE session_id = 'test-session-123'")
    assert cursor.fetchone() is None
    conn.close()
