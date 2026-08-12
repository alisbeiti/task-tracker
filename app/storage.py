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
    """Replace all in-memory tasks with the given payloads.

    Args:
        task_payloads: Task dicts (e.g. as previously produced by
            ``save_tasks_to_json``) to load. Existing in-memory tasks
            are cleared first.

    Returns:
        None.
    """
    _tasks.clear()
    for task_payload in task_payloads:
        task = _hydrate_task(task_payload)
        _tasks[task.id] = task


def save_tasks_to_json() -> list[dict]:
    """Serialize all in-memory tasks to JSON-compatible dicts.

    Returns:
        One dict per task, in JSON mode (e.g. datetimes rendered as
        ISO strings).
    """
    return [task.model_dump(mode="json") for task in _tasks.values()]


def add_task(payload: TaskCreate) -> TaskResponse:
    """Create and store a new task.

    Args:
        payload: Validated task-creation fields.

    Returns:
        The newly created task, with a generated ``id`` and
        ``created_at``/``updated_at`` set to the current UTC time.
    """
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


def get_all_tasks(
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    search: Optional[str] = None,
    assignee: Optional[str] = None,
) -> list[TaskResponse]:
    """Return in-memory tasks matching the given filters.

    Args:
        status: If provided, only tasks with this exact status are kept.
        priority: If provided, only tasks with this exact priority are
            kept.
        search: If provided, a case-insensitive substring match against
            each task's ``title`` and ``description``; blank/whitespace-
            only values are treated as no filter.
        assignee: If provided, a case-insensitive substring match
            against each task's ``assignee``; blank/whitespace-only
            values are treated as no filter, and tasks with no assignee
            never match.

    Returns:
        Matching tasks, sorted by ``created_at`` ascending.
    """
    tasks = list(_tasks.values())

    if status is not None:
        tasks = [task for task in tasks if task.status == status]
    if priority is not None:
        tasks = [task for task in tasks if task.priority == priority]

    if search is not None:
        normalized_search = search.strip().lower()
        if normalized_search:
            tasks = [
                task
                for task in tasks
                if normalized_search in task.title.lower()
                or normalized_search in task.description.lower()
            ]

    if assignee is not None:
        normalized_assignee = assignee.strip().lower()
        if normalized_assignee:
            tasks = [
                task
                for task in tasks
                if task.assignee is not None and normalized_assignee in task.assignee.lower()
            ]

    return sorted(tasks, key=lambda task: task.created_at)


def get_task_by_id(task_id: str) -> Optional[TaskResponse]:
    """Look up a task by id.

    Args:
        task_id: The task's unique identifier.

    Returns:
        The matching task, or ``None`` if no task with ``task_id``
        exists.
    """
    return _tasks.get(task_id)


def update_task(task_id: str, payload: TaskUpdate) -> Optional[TaskResponse]:
    """Apply a partial update to an existing task.

    Only fields explicitly set on ``payload`` are applied (via
    ``model_dump(exclude_unset=True)``); fields omitted from the
    request are left unchanged. If ``payload`` has no fields set, the
    existing task is returned unchanged.

    [VERIFY]: an explicit ``null`` for a nullable field (e.g.
    ``assignee``) counts as "set" under ``exclude_unset`` and will
    clear the field. Confirm this is the intended behavior vs.
    treating ``null`` as "no change".

    Args:
        task_id: The task's unique identifier.
        payload: Fields to update.

    Returns:
        The updated task, or ``None`` if no task with ``task_id``
        exists.
    """
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
    """Delete a task by id.

    Args:
        task_id: The task's unique identifier.

    Returns:
        True if a task was deleted, False if no task with ``task_id``
        existed.
    """
    return _tasks.pop(task_id, None) is not None


def add_comment(task_id: str, text: str) -> Optional[Comment]:
    """Add a comment to an existing task.

    Args:
        task_id: The task's unique identifier.
        text: Raw comment text; leading/trailing whitespace is
            stripped.

    Returns:
        The newly created comment, or ``None`` if no task with
        ``task_id`` exists.

    Raises:
        ValueError: If the stripped text is empty.
    """
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
    """List comments on a task.

    Args:
        task_id: The task's unique identifier.

    Returns:
        The task's comments, or ``None`` if no task with ``task_id``
        exists.
    """
    existing_task = _tasks.get(task_id)
    if existing_task is None:
        return None
    return list(existing_task.comments)


def delete_comment(task_id: str, comment_id: str) -> bool:
    """Delete a single comment from a task.

    Args:
        task_id: The task's unique identifier.
        comment_id: The comment's unique identifier.

    Returns:
        True if a comment was deleted, False if the task does not
        exist or the comment was not found on that task.
    """
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
