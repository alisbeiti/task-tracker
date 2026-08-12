import unittest

from fastapi.testclient import TestClient

from app import storage
from app.main import app
from app.models import TaskCreate, TaskPriority, TaskStatus


class StatusTransitionTests(unittest.TestCase):
    def setUp(self) -> None:
        storage._reset()
        self.client = TestClient(app)

    def test_patch_allows_valid_transition(self) -> None:
        create_response = self.client.post(
            "/tasks",
            json={"title": "Write docs", "status": TaskStatus.TODO.value},
        )
        self.assertEqual(create_response.status_code, 201)
        task_id = create_response.json()["id"]

        response = self.client.patch(
            f"/tasks/{task_id}",
            json={"status": TaskStatus.IN_PROGRESS.value},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], TaskStatus.IN_PROGRESS.value)

    def test_patch_rejects_invalid_transition(self) -> None:
        create_response = self.client.post(
            "/tasks",
            json={"title": "Ship feature", "status": TaskStatus.TODO.value},
        )
        self.assertEqual(create_response.status_code, 201)
        task_id = create_response.json()["id"]

        response = self.client.patch(
            f"/tasks/{task_id}",
            json={"status": TaskStatus.DONE.value},
        )

        self.assertEqual(response.status_code, 422)
        self.assertIn("Invalid status transition", response.json()["detail"])

    def test_patch_allows_same_status_when_priority_changes(self) -> None:
        create_response = self.client.post(
            "/tasks",
            json={"title": "Triage bug", "status": TaskStatus.TODO.value},
        )
        self.assertEqual(create_response.status_code, 201)
        task_id = create_response.json()["id"]

        response = self.client.patch(
            f"/tasks/{task_id}",
            json={
                "status": TaskStatus.TODO.value,
                "priority": TaskPriority.HIGH.value,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], TaskStatus.TODO.value)
        self.assertEqual(response.json()["priority"], TaskPriority.HIGH.value)

    def test_patch_allows_done_to_in_progress(self) -> None:
        create_response = self.client.post(
            "/tasks",
            json={"title": "Reopen bug", "status": TaskStatus.DONE.value},
        )
        self.assertEqual(create_response.status_code, 201)
        task_id = create_response.json()["id"]

        response = self.client.patch(
            f"/tasks/{task_id}",
            json={"status": TaskStatus.IN_PROGRESS.value},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], TaskStatus.IN_PROGRESS.value)

    def test_patch_rejects_done_to_todo(self) -> None:
        create_response = self.client.post(
            "/tasks",
            json={"title": "Ship feature", "status": TaskStatus.DONE.value},
        )
        self.assertEqual(create_response.status_code, 201)
        task_id = create_response.json()["id"]

        response = self.client.patch(
            f"/tasks/{task_id}",
            json={"status": TaskStatus.TODO.value},
        )

        self.assertEqual(response.status_code, 422)
        self.assertIn("Invalid status transition", response.json()["detail"])

    def test_patch_rejects_in_progress_to_todo(self) -> None:
        create_response = self.client.post(
            "/tasks",
            json={"title": "Triage bug", "status": TaskStatus.IN_PROGRESS.value},
        )
        self.assertEqual(create_response.status_code, 201)
        task_id = create_response.json()["id"]

        response = self.client.patch(
            f"/tasks/{task_id}",
            json={"status": TaskStatus.TODO.value},
        )

        self.assertEqual(response.status_code, 422)
        self.assertIn("Invalid status transition", response.json()["detail"])

    def test_patch_skips_validation_when_status_not_provided(self) -> None:
        create_response = self.client.post(
            "/tasks",
            json={"title": "Review PR", "status": TaskStatus.TODO.value},
        )
        self.assertEqual(create_response.status_code, 201)
        task_id = create_response.json()["id"]

        response = self.client.patch(
            f"/tasks/{task_id}",
            json={"title": "Review PR again"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "Review PR again")


if __name__ == "__main__":
    unittest.main()
