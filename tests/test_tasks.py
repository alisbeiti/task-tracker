from fastapi.testclient import TestClient


def test_create_task_valid_returns_201_with_full_body(client: TestClient) -> None:
    response = client.post(
        "/tasks",
        json={
            "title": "Write docs",
            "description": "Draft the API docs",
            "status": "ToDo",
            "priority": "High",
            "assignee": "Alice",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["title"] == "Write docs"
    assert payload["description"] == "Draft the API docs"
    assert payload["status"] == "ToDo"
    assert payload["priority"] == "High"
    assert payload["assignee"] == "Alice"
    assert payload["id"]
    assert payload["created_at"]
    assert payload["updated_at"]


def test_create_task_missing_title_returns_422(client: TestClient) -> None:
    response = client.post("/tasks", json={})

    assert response.status_code == 422
    assert response.json()["detail"]


def test_create_task_blank_title_returns_422(client: TestClient) -> None:
    response = client.post("/tasks", json={"title": "   "})

    assert response.status_code == 422
    assert response.json()["detail"]


def test_create_task_invalid_priority_returns_422(client: TestClient) -> None:
    response = client.post("/tasks", json={"title": "Bad priority", "priority": "Urgent"})

    assert response.status_code == 422
    assert response.json()["detail"]


def test_create_task_unknown_field_returns_422(client: TestClient) -> None:
    response = client.post("/tasks", json={"title": "Extra", "unexpected": 1})

    assert response.status_code == 422
    assert response.json()["detail"]


def test_list_tasks_empty_returns_200_and_empty_list(client: TestClient) -> None:
    response = client.get("/tasks")

    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_filter_by_status_no_match_returns_200_and_empty_list(client: TestClient) -> None:
    client.post("/tasks", json={"title": "One"})
    response = client.get("/tasks", params={"status": "Done"})

    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_filter_by_priority_returns_only_matches(client: TestClient) -> None:
    client.post("/tasks", json={"title": "Low task", "priority": "Low"})
    client.post("/tasks", json={"title": "High task", "priority": "High"})

    response = client.get("/tasks", params={"priority": "High"})

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["title"] == "High task"
    assert payload[0]["priority"] == "High"


def test_get_task_by_id_returns_task(client: TestClient, created_task: dict) -> None:
    response = client.get(f"/tasks/{created_task['id']}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == created_task["id"]
    assert payload["title"] == "fixture task"


def test_get_task_by_id_not_found_returns_404_with_detail(client: TestClient) -> None:
    response = client.get("/tasks/missing-id")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task with id missing-id not found"


def test_patch_partial_update_keeps_other_fields(client: TestClient, created_task: dict) -> None:
    response = client.patch(
        f"/tasks/{created_task['id']}",
        json={"title": "Updated title"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["title"] == "Updated title"
    assert payload["description"] == ""
    assert payload["priority"] == "Medium"
    assert payload["assignee"] is None


def test_patch_not_found_returns_404(client: TestClient) -> None:
    response = client.patch("/tasks/missing-id", json={"title": "Updated title"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Task with id missing-id not found"


def test_patch_valid_transition_todo_to_inprogress_returns_200(client: TestClient, created_task: dict) -> None:
    response = client.patch(
        f"/tasks/{created_task['id']}",
        json={"status": "InProgress"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "InProgress"


def test_patch_invalid_transition_todo_to_done_returns_422(client: TestClient, created_task: dict) -> None:
    response = client.patch(
        f"/tasks/{created_task['id']}",
        json={"status": "Done"},
    )

    assert response.status_code == 422
    assert "Invalid status transition" in response.json()["detail"]


def test_patch_same_status_returns_422(client: TestClient, created_task: dict) -> None:
    response = client.patch(
        f"/tasks/{created_task['id']}",
        json={"status": "ToDo"},
    )

    assert response.status_code == 422
    assert "Invalid status transition" in response.json()["detail"]


def test_delete_existing_returns_204_no_body(client: TestClient, created_task: dict) -> None:
    response = client.delete(f"/tasks/{created_task['id']}")

    assert response.status_code == 204
    assert response.content == b""


def test_delete_missing_returns_404(client: TestClient) -> None:
    response = client.delete("/tasks/missing-id")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task with id missing-id not found"
