import reflex as rx
from typing import List, Optional
from datetime import datetime
from sqlmodel import Field
from sqlalchemy import UniqueConstraint, Column, String, DateTime
import pendulum
from pendulum import Timezone


@rx.serializer
def serialize_datetime(value: datetime) -> str:
    if isinstance(value, str):
        return value
    return value.isoformat()


class User(rx.Model, table=True):
    """User model for OIDC authentication."""

    sub: str = Field(unique=True, index=True)
    email: str = Field(index=True)
    name: str = ""
    picture: str = ""
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=pendulum.local_timezone()),
        sa_column=Column(DateTime(timezone=True)),
    )


class Repository(rx.Model, table=True):
    """A list of repositories to manage."""

    name: str
    description: str
    order_index: int = Field(default=0)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=pendulum.local_timezone()),
        sa_column=Column(DateTime(timezone=True)),
    )

    __table_args__ = (UniqueConstraint("name", name="unique_repository_name"),)


class Diagram(rx.Model, table=True):
    """Diagrams associated with a repository."""

    repository_id: int
    name: str
    content: str  # Code for PlantUML/Mermaid or Base64 for Draw.io
    diagram_type: str  # "plantuml", "mermaid", "drawio"
    category: str  # "as-is", "to-be"
    notes: str = ""  # Markdown notes
    last_ai_prompt: str = ""
    last_ai_notes_prompt: str = ""
    order_index: int = Field(default=0)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=pendulum.local_timezone()),
        sa_column=Column(DateTime(timezone=True)),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=pendulum.local_timezone()),
        sa_column=Column(DateTime(timezone=True)),
    )

    __table_args__ = (
        UniqueConstraint("repository_id", "name", name="unique_diagram_per_repository"),
    )
