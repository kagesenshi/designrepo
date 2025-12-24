import reflex as rx
from .models import Project, Diagram
from typing import List, Optional
import openai
import os
from datetime import datetime
import urllib.parse
import zlib
import base64
import pendulum
import pydantic


class ProjectSchema(pydantic.BaseModel):
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    created_at: Optional[datetime] = None


class DiagramSchema(pydantic.BaseModel):
    id: Optional[int] = None
    project_id: Optional[int] = None
    name: str = ""
    content: str = ""
    diagram_type: str = "plantuml"
    category: str = "to-be"
    notes: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class State(rx.State):
    """The base state for the app."""

    projects: List[ProjectSchema] = []
    current_project: Optional[ProjectSchema] = None

    diagrams: List[DiagramSchema] = []
    current_diagram: Optional[DiagramSchema] = None

    # Form fields
    project_name: str = ""
    project_description: str = ""

    diagram_name: str = ""
    diagram_content: str = ""
    diagram_type: str = "plantuml"
    diagram_category: str = "to-be"
    diagram_notes: str = ""

    # Modal visibility
    show_project_modal: bool = False
    show_diagram_modal: bool = False

    # OpenAI
    ai_prompt: str = ""
    is_loading: bool = False
    show_ai_modal: bool = False

    def toggle_ai_modal(self):
        self.show_ai_modal = not self.show_ai_modal
        if not self.show_ai_modal:
            self.ai_prompt = ""

    def set_project_name(self, value: str):
        self.project_name = value

    def set_project_description(self, value: str):
        self.project_description = value

    def set_diagram_name(self, value: str):
        self.diagram_name = value

    def set_diagram_content(self, value: str):
        self.diagram_content = value

    def set_diagram_type(self, value: str):
        self.diagram_type = value

    def set_diagram_category(self, value: str):
        self.diagram_category = value

    def set_diagram_notes(self, value: str):
        self.diagram_notes = value

    def set_ai_prompt(self, value: str):
        self.ai_prompt = value

    @rx.var
    def plantuml_url(self) -> str:
        if not self.diagram_content or self.diagram_type != "plantuml":
            return ""
        try:
            hex_data = self.diagram_content.encode("utf-8").hex()
            return f"http://www.plantuml.com/plantuml/svg/~h{hex_data}"
        except:
            return ""

    @rx.var
    def drawio_url(self) -> str:
        if not self.diagram_content or self.diagram_type != "drawio":
            return ""
        try:
            encoded_xml = urllib.parse.quote(self.diagram_content)
            return f"https://viewer.diagrams.net/?xml={encoded_xml}"
        except:
            return ""

    @rx.var
    def mermaid_url(self) -> str:
        if not self.diagram_content or self.diagram_type != "mermaid":
            return ""
        try:
            # Mermaid encoding for mermaid.ink
            content_bytes = self.diagram_content.encode("utf-8")
            base64_content = base64.b64encode(content_bytes).decode("utf-8")
            return f"https://mermaid.ink/svg/{base64_content}"
        except:
            return ""

    def load_projects(self):
        with rx.session() as session:
            db_projects = session.exec(Project.select()).all()
            self.projects = [
                ProjectSchema(
                    id=p.id,
                    name=p.name,
                    description=p.description,
                    created_at=p.created_at,
                )
                for p in db_projects
            ]

    def add_project(self):
        if not self.project_name:
            return rx.toast.error("Project name is required")
        with rx.session() as session:
            # Check for duplicate project name
            existing = session.exec(
                Project.select().where(Project.name == self.project_name)
            ).first()
            if existing:
                return rx.toast.error(f"Project '{self.project_name}' already exists.")

            project = Project(
                name=self.project_name, description=self.project_description
            )
            session.add(project)
            session.commit()
            session.refresh(project)
            self.load_projects()
            self.project_name = ""
            self.project_description = ""
            self.show_project_modal = False

    def select_project(self, project: ProjectSchema):
        self.current_project = project
        self.load_diagrams()

    def load_diagrams(self):
        if not self.current_project:
            return
        with rx.session() as session:
            db_diagrams = session.exec(
                Diagram.select().where(Diagram.project_id == self.current_project.id)
            ).all()
            self.diagrams = [
                DiagramSchema(
                    id=d.id,
                    project_id=d.project_id,
                    name=d.name,
                    content=d.content,
                    diagram_type=d.diagram_type,
                    category=d.category,
                    notes=d.notes,
                    created_at=d.created_at,
                    updated_at=d.updated_at,
                )
                for d in db_diagrams
            ]

    def add_diagram(self):
        if not self.current_project:
            return
        if not self.diagram_name:
            return rx.toast.error("Diagram name is required")

        with rx.session() as session:
            # Check for duplicate diagram name in the same project
            existing = session.exec(
                Diagram.select().where(
                    (Diagram.project_id == self.current_project.id)
                    & (Diagram.name == self.diagram_name)
                )
            ).first()
            if existing:
                return rx.toast.error(
                    f"Diagram '{self.diagram_name}' already exists in this project."
                )

            diagram = Diagram(
                project_id=self.current_project.id,
                name=self.diagram_name,
                content=self.diagram_content,
                diagram_type=self.diagram_type,
                category=self.diagram_category,
                notes=self.diagram_notes,
            )
            session.add(diagram)
            session.commit()
            self.load_diagrams()
            self.diagram_name = ""
            self.diagram_content = ""
            self.diagram_notes = ""
            self.show_diagram_modal = False

    def select_diagram(self, diagram: DiagramSchema):
        self.current_diagram = diagram
        self.diagram_name = diagram.name
        self.diagram_content = diagram.content
        self.diagram_type = diagram.diagram_type
        self.diagram_category = diagram.category
        self.diagram_notes = diagram.notes

    def save_diagram(self):
        if not self.current_diagram:
            return
        if not self.diagram_name:
            return rx.toast.error("Diagram name is required")

        with rx.session() as session:
            # Check for duplicate diagram name (excluding the current one)
            existing = session.exec(
                Diagram.select().where(
                    (Diagram.project_id == self.current_diagram.project_id)
                    & (Diagram.name == self.diagram_name)
                    & (Diagram.id != self.current_diagram.id)
                )
            ).first()
            if existing:
                return rx.toast.error(
                    f"Another diagram named '{self.diagram_name}' already exists in this project."
                )

            diagram = session.exec(
                Diagram.select().where(Diagram.id == self.current_diagram.id)
            ).first()
            diagram.name = self.diagram_name
            diagram.content = self.diagram_content
            diagram.diagram_type = self.diagram_type
            diagram.category = self.diagram_category
            diagram.notes = self.diagram_notes
            diagram.updated_at = datetime.now(tz=pendulum.local_timezone())
            session.add(diagram)
            session.commit()
            session.refresh(diagram)
            self.load_diagrams()
            # Update current diagram in state to reflect changes
            self.current_diagram = DiagramSchema(
                id=diagram.id,
                project_id=diagram.project_id,
                name=diagram.name,
                content=diagram.content,
                diagram_type=diagram.diagram_type,
                category=diagram.category,
                notes=diagram.notes,
                created_at=diagram.created_at,
                updated_at=diagram.updated_at,
            )

    async def generate_diagram(self):
        if not self.ai_prompt:
            return
        self.is_loading = True
        self.show_ai_modal = False
        yield

        try:
            client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            system_msg = f"Generate or modify {self.diagram_type} code based on the user instruction. "
            if self.diagram_type == "plantuml":
                system_msg += "Only return the code block without backticks."
            else:
                system_msg += "Return the code block with backticks."

            user_content = f"Instruction: {self.ai_prompt}\n"
            if self.diagram_content:
                user_content += f"Current Diagram Code:\n{self.diagram_content}"

            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": system_msg,
                    },
                    {"role": "user", "content": user_content},
                ],
            )
            content = response.choices[0].message.content
            # Clean up content if it has backticks
            if content.startswith("```"):
                content = "\n".join(content.split("\n")[1:-1])
            self.diagram_content = content
            self.ai_prompt = ""
        except Exception as e:
            yield rx.toast.error(f"Error generating diagram: {str(e)}")
        finally:
            self.is_loading = False
            yield

    async def generate_notes(self):
        if not self.diagram_content:
            return
        self.is_loading = True
        yield

        try:
            client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "Generate markdown documentation/notes for the following diagram code.",
                    },
                    {"role": "user", "content": self.diagram_content},
                ],
            )
            self.diagram_notes = response.choices[0].message.content
        except Exception as e:
            yield rx.toast.error(f"Error generating notes: {str(e)}")
        finally:
            self.is_loading = False
            yield

    async def handle_upload(self, files: List[rx.UploadFile]):
        """Handle uploading a Draw.io file."""
        for file in files:
            upload_data = await file.read()
            # For Draw.io, we store the content (which is XML)
            self.diagram_content = upload_data.decode("utf-8")
            self.diagram_type = "drawio"
            if not self.diagram_name:
                self.diagram_name = file.filename
