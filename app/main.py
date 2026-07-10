from fastapi import FastAPI, HTTPException, status

from app import storage
from app.api import health
from app.business_rules import validate_status_transition
from app.database import init_db
from app.models import TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate

app = FastAPI(
    title="Task Tracker API",
    description="Module 1 Task Tracker REST API skeleton.",
    version="0.1.0",
)

#post endpoint to create a new task

@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["tasks"])
def create_task(payload: TaskCreate) -> TaskResponse:
    return storage.add_task(payload)

#get endpoint to list all tasks with optional filters for status and priority
@app.get("/tasks", response_model=list[TaskResponse], tags=["tasks"])
def list_tasks(status: TaskStatus | None = None, priority: TaskPriority | None = None) -> list[TaskResponse]:
    return storage.get_all_tasks(status=status, priority=priority)

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
@app.delete("/tasks/{task_id}", status_code=status.HTTP_200_OK, tags=["tasks"])
def delete_task(task_id: str) -> dict[str, str]:
    deleted = storage.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return {"message": "Task deleted successfully"}


@app.on_event("startup")
def on_startup() -> None:
    """
    Ensure the SQLite database file and (currently empty) schema
    exist before the application starts serving requests.
    """
    init_db()


app.include_router(health.router)