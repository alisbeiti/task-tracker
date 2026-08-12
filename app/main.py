from fastapi import FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, field_validator

from app import storage
from app.api import health
from app.business_rules import validate_status_transition
from app.database import init_db
from app.models import Comment, TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate


class CommentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        """Strip surrounding whitespace and reject blank comment text.

        Args:
            value: Raw ``text`` field value supplied for a new comment.

        Returns:
            The stripped comment text.

        Raises:
            ValueError: If the stripped value is empty, which FastAPI/
                Pydantic surfaces to the client as a 422 response.
        """
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError("comment cannot be blank")
        return cleaned_value

app = FastAPI(
    title="Task Tracker API",
    description="Module 1 Task Tracker REST API skeleton.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["tasks"])
def create_task(payload: TaskCreate) -> TaskResponse:
    """Create a new task.

    Args:
        payload: Task fields to create. ``status`` defaults to ``ToDo``
            and ``priority`` defaults to ``Medium`` if omitted.

    Returns:
        The newly created task, including its generated ``id``,
        ``created_at``/``updated_at`` timestamps, and an empty
        ``comments`` list.

    Example:
        ``POST /tasks`` with body ``{"title": "Write docs"}`` returns
        ``201`` and the created task.
    """
    return storage.add_task(payload)

@app.get("/tasks", response_model=list[TaskResponse], tags=["tasks"])
def list_tasks(
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    search: str | None = None,
    assignee: str | None = None,
) -> list[TaskResponse]:
    """List tasks, optionally filtered by status, priority, assignee, and search text.

    Args:
        status: If provided, only tasks with this exact status are
            returned.
        priority: If provided, only tasks with this exact priority are
            returned.
        search: If provided, a case-insensitive substring match against
            each task's ``title`` and ``description``. Blank/whitespace-
            only values are treated as no filter.
        assignee: If provided, a case-insensitive substring match
            against each task's ``assignee``. Blank/whitespace-only
            values are treated as no filter; tasks with no assignee
            never match.

    Returns:
        Tasks matching all supplied filters, sorted by ``created_at``
        ascending.

    Example:
        ``GET /tasks?status=ToDo&search=docs`` returns open tasks whose
        title or description contains "docs".
    """
    return storage.get_all_tasks(status=status, priority=priority, search=search, assignee=assignee)

@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def get_task(task_id: str) -> TaskResponse:
    """Retrieve a single task by id.

    Args:
        task_id: The task's unique identifier.

    Returns:
        The matching task.

    Raises:
        HTTPException: 404 if no task with ``task_id`` exists.

    Example:
        ``GET /tasks/{task_id}`` returns ``200`` with the task, or
        ``404`` if it doesn't exist.
    """
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return task

@app.patch("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def update_task(task_id: str, payload: TaskUpdate) -> TaskResponse:
    """Partially update a task.

    Only fields present in ``payload`` are changed; omitted fields are
    left as-is. If ``status`` is included, the transition from the
    task's current status to the new status must be valid (see
    ``business_rules.validate_status_transition``); setting status to
    its current value is always allowed.

    Args:
        task_id: The task's unique identifier.
        payload: Fields to update.

    Returns:
        The updated task.

    Raises:
        HTTPException: 404 if no task with ``task_id`` exists.
        HTTPException: 422 if ``payload.status`` is an invalid
            transition from the task's current status.
    """
    if payload.status is not None:
        existing_task = storage.get_task_by_id(task_id)
        if existing_task is None:
            raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
        validate_status_transition(existing_task.status, payload.status)

    task = storage.update_task(task_id, payload)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tasks"])
def delete_task(task_id: str) -> Response:
    """Delete a task by id.

    Args:
        task_id: The task's unique identifier.

    Returns:
        An empty ``204 No Content`` response.

    Raises:
        HTTPException: 404 if no task with ``task_id`` exists.
    """
    deleted = storage.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/tasks/{task_id}/comments", response_model=list[Comment], tags=["tasks"])
def list_task_comments(task_id: str) -> list[Comment]:
    """List all comments on a task.

    Args:
        task_id: The task's unique identifier.

    Returns:
        The task's comments.

    Raises:
        HTTPException: 404 if no task with ``task_id`` exists.
    """
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")

    comments = storage.get_task_comments(task_id)
    if comments is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return comments


@app.post("/tasks/{task_id}/comments", response_model=Comment, status_code=status.HTTP_201_CREATED, tags=["tasks"])
def add_task_comment(task_id: str, payload: CommentCreate) -> Comment:
    """Add a comment to a task.

    Args:
        task_id: The task's unique identifier.
        payload: Comment text to add; blank text is rejected by
            ``CommentCreate`` validation before this handler runs.

    Returns:
        The newly created comment.

    Raises:
        HTTPException: 404 if no task with ``task_id`` exists.

    Example:
        ``POST /tasks/{task_id}/comments`` with body ``{"text": "..."}``
        returns ``201`` and the created comment.
    """
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")

    comment = storage.add_comment(task_id, payload.text)
    if comment is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return comment


@app.delete("/tasks/{task_id}/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tasks"])
def delete_task_comment(task_id: str, comment_id: str) -> Response:
    """Delete a single comment from a task.

    Args:
        task_id: The task's unique identifier.
        comment_id: The comment's unique identifier.

    Returns:
        An empty ``204 No Content`` response.

    Raises:
        HTTPException: 404 if ``task_id`` does not exist, or if
            ``comment_id`` does not exist on that task.
    """
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")

    deleted = storage.delete_comment(task_id, comment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Comment with id {comment_id} not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.on_event("startup")
def on_startup() -> None:
    """Ensure the SQLite database file and (currently empty) schema exist.

    Runs once at application startup, before requests are served.

    Returns:
        None.
    """
    init_db()


@app.get("/version", tags=["meta"])
def get_version() -> dict:
    """Return the running API version.

    Returns:
        A dict with a single ``version`` key set to the FastAPI app's
        configured version string.

    Example:
        ``GET /version`` returns ``{"version": "0.1.0"}``.
    """
    return {"version": app.version}


app.include_router(health.router)