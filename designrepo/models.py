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


class Repository(rx.Model, table=True):
    """A list of repositories to manage."""

    name: str
    description: str
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
