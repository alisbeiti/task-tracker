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


def test_list_tasks_search_by_title_returns_only_matching_tasks(client: TestClient) -> None:
    client.post("/tasks", json={"title": "Plan launch", "description": "Outline the rollout"})
    client.post("/tasks", json={"title": "Write docs", "description": "Draft the help content"})

    response = client.get("/tasks", params={"search": "launch"})

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["title"] == "Plan launch"


def test_list_tasks_search_by_description_returns_only_matching_tasks(client: TestClient) -> None:
    client.post("/tasks", json={"title": "Alpha", "description": "Draft API docs"})
    client.post("/tasks", json={"title": "Beta", "description": "Plan the release"})

    response = client.get("/tasks", params={"search": "api"})

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["title"] == "Alpha"
    assert payload[0]["description"] == "Draft API docs"


def test_list_tasks_filter_by_status_returns_only_matching_tasks(client: TestClient) -> None:
    client.post("/tasks", json={"title": "To do task", "status": "ToDo"})
    client.post("/tasks", json={"title": "In progress task", "status": "InProgress"})

    response = client.get("/tasks", params={"status": "InProgress"})

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["title"] == "In progress task"
    assert payload[0]["status"] == "InProgress"


def test_list_tasks_filter_by_assignee_returns_only_matching_tasks(client: TestClient) -> None:
    client.post("/tasks", json={"title": "Alice task", "assignee": "Alice"})
    client.post("/tasks", json={"title": "Bob task", "assignee": "Bob"})

    response = client.get("/tasks", params={"assignee": "alice"})

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["title"] == "Alice task"
    assert payload[0]["assignee"] == "Alice"


def test_list_tasks_combines_multiple_filters(client: TestClient) -> None:
    client.post("/tasks", json={"title": "High todo task", "status": "ToDo", "priority": "High"})
    client.post("/tasks", json={"title": "High in progress task", "status": "InProgress", "priority": "High"})
    client.post("/tasks", json={"title": "Low todo task", "status": "ToDo", "priority": "Low"})

    response = client.get("/tasks", params={"status": "ToDo", "priority": "High"})

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["title"] == "High todo task"
    assert payload[0]["status"] == "ToDo"
    assert payload[0]["priority"] == "High"


def test_list_tasks_combines_search_with_filters(client: TestClient) -> None:
    client.post(
        "/tasks",
        json={"title": "Plan implementation", "description": "Discuss rollout", "status": "InProgress", "priority": "High", "assignee": "Dana"},
    )
    client.post(
        "/tasks",
        json={"title": "Plan support", "description": "Discuss rollout", "status": "InProgress", "priority": "Low", "assignee": "Dana"},
    )

    response = client.get("/tasks", params={"search": "plan", "status": "InProgress", "priority": "High", "assignee": "dana"})

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["title"] == "Plan implementation"


def test_list_tasks_no_matches_returns_200_and_empty_list(client: TestClient) -> None:
    client.post("/tasks", json={"title": "Existing task"})

    response = client.get("/tasks", params={"search": "missing"})

    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_invalid_filter_value_returns_422(client: TestClient) -> None:
    response = client.get("/tasks", params={"priority": "Urgent"})

    assert response.status_code == 422
    assert response.json()["detail"]


def test_list_tasks_without_query_parameters_returns_all_tasks(client: TestClient) -> None:
    client.post("/tasks", json={"title": "First task"})
    client.post("/tasks", json={"title": "Second task"})

    response = client.get("/tasks")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2
    assert {item["title"] for item in payload} == {"First task", "Second task"}


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


def test_patch_invalid_status_value_pending_returns_422(client: TestClient) -> None:
    created_response = client.post("/tasks", json={"title": "Example task"})
    task_id = created_response.json()["id"]

    response = client.patch(f"/tasks/{task_id}", json={"status": "Pending"})

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail
    assert "Pending" in str(detail)


def test_delete_existing_returns_204_no_body(client: TestClient, created_task: dict) -> None:
    response = client.delete(f"/tasks/{created_task['id']}")

    assert response.status_code == 204
    assert response.content == b""


def test_delete_missing_returns_404(client: TestClient) -> None:
    response = client.delete("/tasks/missing-id")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task with id missing-id not found"


def test_list_task_comments_returns_existing_comments(client: TestClient, created_task: dict) -> None:
    client.post(f"/tasks/{created_task['id']}/comments", json={"text": "First comment"})
    client.post(f"/tasks/{created_task['id']}/comments", json={"text": "Second comment"})

    response = client.get(f"/tasks/{created_task['id']}/comments")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2
    assert [item["text"] for item in payload] == ["First comment", "Second comment"]


def test_add_task_comment_returns_201_with_comment_payload(client: TestClient, created_task: dict) -> None:
    response = client.post(f"/tasks/{created_task['id']}/comments", json={"text": "New note"})

    assert response.status_code == 201
    payload = response.json()
    assert payload["task_id"] == created_task["id"]
    assert payload["text"] == "New note"
    assert payload["id"]
    assert payload["created_at"]


def test_delete_task_comment_returns_204_no_body(client: TestClient, created_task: dict) -> None:
    create_response = client.post(f"/tasks/{created_task['id']}/comments", json={"text": "Delete me"})
    comment_id = create_response.json()["id"]

    response = client.delete(f"/tasks/{created_task['id']}/comments/{comment_id}")

    assert response.status_code == 204
    assert response.content == b""


def test_add_task_comment_blank_text_returns_422(client: TestClient, created_task: dict) -> None:
    for blank_value in ["", "   "]:
        response = client.post(f"/tasks/{created_task['id']}/comments", json={"text": blank_value})

        assert response.status_code == 422
        assert response.json()["detail"]


def test_list_task_comments_task_not_found_returns_404(client: TestClient) -> None:
    response = client.get("/tasks/missing-id/comments")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task with id missing-id not found"


def test_delete_task_comment_comment_not_found_returns_404(client: TestClient, created_task: dict) -> None:
    response = client.delete(f"/tasks/{created_task['id']}/comments/missing-comment")

    assert response.status_code == 404
    assert response.json()["detail"] == "Comment with id missing-comment not found"
