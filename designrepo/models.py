import reflex as rx
from typing import List, Optional
from datetime import datetime
from sqlalchemy import UniqueConstraint, Column, String


class Project(rx.Model, table=True):
    """A list of projects to manage."""

    name: str
    description: str
    created_at: datetime = datetime.now()

    __table_args__ = (UniqueConstraint("name", name="unique_project_name"),)


class Diagram(rx.Model, table=True):
    """Diagrams associated with a project."""

    project_id: int
    name: str
    content: str  # Code for PlantUML/Mermaid or Base64 for Draw.io
    diagram_type: str  # "plantuml", "mermaid", "drawio"
    category: str  # "as-is", "to-be"
    notes: str = ""  # Markdown notes
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    __table_args__ = (
        UniqueConstraint("project_id", "name", name="unique_diagram_per_project"),
    )
