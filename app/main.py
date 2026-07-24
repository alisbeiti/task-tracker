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

#post endpoint to create a new task

@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["tasks"])
def create_task(payload: TaskCreate) -> TaskResponse:
    return storage.add_task(payload)

#get endpoint to list all tasks with optional filters for status, priority, assignee and text search
@app.get("/tasks", response_model=list[TaskResponse], tags=["tasks"])
def list_tasks(
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    search: str | None = None,
    assignee: str | None = None,
) -> list[TaskResponse]:
    return storage.get_all_tasks(status=status, priority=priority, search=search, assignee=assignee)

#get endpoint to retrieve a specific task by its ID
@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def get_task(task_id: str) -> TaskResponse:
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return task

#patch endpoint to update a specific task by its ID
@app.patch("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def update_task(task_id: str, payload: TaskUpdate) -> TaskResponse:
    if payload.status is not None:
        existing_task = storage.get_task_by_id(task_id)
        if existing_task is None:
            raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
        validate_status_transition(existing_task.status, payload.status)

    task = storage.update_task(task_id, payload)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return task

#delete endpoint to delete a specific task by its ID
@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tasks"])
def delete_task(task_id: str) -> Response:
    deleted = storage.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/tasks/{task_id}/comments", response_model=list[Comment], tags=["tasks"])
def list_task_comments(task_id: str) -> list[Comment]:
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")

    comments = storage.get_task_comments(task_id)
    if comments is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return comments


@app.post("/tasks/{task_id}/comments", response_model=Comment, status_code=status.HTTP_201_CREATED, tags=["tasks"])
def add_task_comment(task_id: str, payload: CommentCreate) -> Comment:
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")

    comment = storage.add_comment(task_id, payload.text)
    if comment is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return comment


@app.delete("/tasks/{task_id}/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tasks"])
def delete_task_comment(task_id: str, comment_id: str) -> Response:
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")

    deleted = storage.delete_comment(task_id, comment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Comment with id {comment_id} not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.on_event("startup")
def on_startup() -> None:
    """
    Ensure the SQLite database file and (currently empty) schema
    exist before the application starts serving requests.
    """
    init_db()


app.include_router(health.router)