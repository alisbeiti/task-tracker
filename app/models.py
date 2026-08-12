from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TaskStatus(str, Enum):
    TODO = "ToDo"
    IN_PROGRESS = "InProgress"
    DONE = "Done"


class TaskPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


def _validate_title(value: str) -> str:
    cleaned_value = value.strip()
    if not cleaned_value:
        raise ValueError("title cannot be blank")
    if len(cleaned_value) > 200:
        raise ValueError("title must be 200 characters or fewer")
    return cleaned_value


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    description: Optional[str] = ""
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee: Optional[str] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        """Validate and normalize a task title.

        Args:
            value: Raw title value.

        Returns:
            The stripped title.

        Raises:
            ValueError: If the stripped title is empty or exceeds 200
                characters, which FastAPI/Pydantic surfaces to the
                client as a 422 response.
        """
        return _validate_title(value)


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee: Optional[str] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: Optional[str]) -> Optional[str]:
        """Validate and normalize an optional task title update.

        Args:
            value: Raw title value, or ``None`` if the title is not
                being updated.

        Returns:
            ``None`` if ``value`` is ``None``; otherwise the stripped
            title.

        Raises:
            ValueError: If ``value`` is provided but the stripped title
                is empty or exceeds 200 characters.
        """
        if value is None:
            return None
        return _validate_title(value)


class Comment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    task_id: str
    text: str
    created_at: datetime

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        """Strip surrounding whitespace and reject blank comment text.

        Args:
            value: Raw comment text.

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


class TaskResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    assignee: Optional[str]
    created_at: datetime
    updated_at: datetime
    comments: list[Comment] = Field(default_factory=list)
