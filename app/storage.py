from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from app.models import Comment, TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate

_tasks: dict[str, TaskResponse] = {}


def _coerce_comments(comment_data: object, task_id: str) -> list[Comment]:
    if not comment_data:
        return []
    if not isinstance(comment_data, list):
        return []

    comments: list[Comment] = []
    for item in comment_data:
        if isinstance(item, Comment):
            comments.append(item)
        elif isinstance(item, dict):
            payload = dict(item)
            payload.setdefault("id", str(uuid4()))
            payload.setdefault("task_id", task_id)
            payload.setdefault("created_at", datetime.now(timezone.utc))
            comments.append(Comment(**payload))
        else:
            comments.append(
                Comment(
                    id=str(uuid4()),
                    task_id=task_id,
                    text=str(item),
                    created_at=datetime.now(timezone.utc),
                )
            )
    return comments


def _hydrate_task(task_data: dict) -> TaskResponse:
    payload = dict(task_data)
    payload["comments"] = _coerce_comments(payload.get("comments"), payload.get("id") or str(uuid4()))

    if isinstance(payload.get("created_at"), str):
        payload["created_at"] = datetime.fromisoformat(payload["created_at"])
    if isinstance(payload.get("updated_at"), str):
        payload["updated_at"] = datetime.fromisoformat(payload["updated_at"])

    return TaskResponse(**payload)


def _replace_task_comments(task: TaskResponse, comments: list[Comment]) -> TaskResponse:
    updated_data = task.model_dump()
    updated_data["comments"] = comments
    updated_data["updated_at"] = datetime.now(timezone.utc)
    return TaskResponse(**updated_data)


def load_tasks_from_json(task_payloads: list[dict]) -> None:
    _tasks.clear()
    for task_payload in task_payloads:
        task = _hydrate_task(task_payload)
        _tasks[task.id] = task


def save_tasks_to_json() -> list[dict]:
    return [task.model_dump(mode="json") for task in _tasks.values()]


def add_task(payload: TaskCreate) -> TaskResponse:
    now = datetime.now(timezone.utc)
    task = TaskResponse(
        id=str(uuid4()),
        title=payload.title,
        description=payload.description or "",
        status=payload.status,
        priority=payload.priority,
        assignee=payload.assignee,
        created_at=now,
        updated_at=now,
    )
    _tasks[task.id] = task
    return task


def get_all_tasks(status: Optional[TaskStatus] = None, priority: Optional[TaskPriority] = None) -> list[TaskResponse]:
    tasks = list(_tasks.values())
    if status is not None:
        tasks = [task for task in tasks if task.status == status]
    if priority is not None:
        tasks = [task for task in tasks if task.priority == priority]
    return sorted(tasks, key=lambda task: task.created_at)


def get_task_by_id(task_id: str) -> Optional[TaskResponse]:
    return _tasks.get(task_id)


def update_task(task_id: str, payload: TaskUpdate) -> Optional[TaskResponse]:
    existing_task = _tasks.get(task_id)
    if existing_task is None:
        return None

    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        return existing_task

    updated_data = existing_task.model_dump()
    updated_data.update(update_data)
    updated_data["updated_at"] = datetime.now(timezone.utc)

    updated_task = TaskResponse(**updated_data)
    _tasks[task_id] = updated_task
    return updated_task


def delete_task(task_id: str) -> bool:
    return _tasks.pop(task_id, None) is not None


def add_comment(task_id: str, text: str) -> Optional[Comment]:
    existing_task = _tasks.get(task_id)
    if existing_task is None:
        return None

    cleaned_text = text.strip()
    if not cleaned_text:
        raise ValueError("comment cannot be blank")

    comment = Comment(
        id=str(uuid4()),
        task_id=task_id,
        text=cleaned_text,
        created_at=datetime.now(timezone.utc),
    )
    updated_comments = list(existing_task.comments)
    updated_comments.append(comment)
    _tasks[task_id] = _replace_task_comments(existing_task, updated_comments)
    return comment


def get_task_comments(task_id: str) -> Optional[list[Comment]]:
    existing_task = _tasks.get(task_id)
    if existing_task is None:
        return None
    return list(existing_task.comments)


def delete_comment(task_id: str, comment_id: str) -> bool:
    existing_task = _tasks.get(task_id)
    if existing_task is None:
        return False

    updated_comments = [comment for comment in existing_task.comments if comment.id != comment_id]
    if len(updated_comments) == len(existing_task.comments):
        return False

    _tasks[task_id] = _replace_task_comments(existing_task, updated_comments)
    return True


def _reset() -> None:
    _tasks.clear()
