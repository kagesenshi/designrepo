import reflex as rx
from .models import Project, Diagram
from typing import List, Optional
import openai
import os
from datetime import datetime
import urllib.parse
import zlib
import base64


class State(rx.State):
    """The base state for the app."""

    projects: List[Project] = []
    current_project: Optional[Project] = None

    diagrams: List[Diagram] = []
    current_diagram: Optional[Diagram] = None

    # Form fields
    project_name: str = ""
    project_description: str = ""

    diagram_name: str = ""
    diagram_content: str = ""
    diagram_type: str = "plantuml"
    diagram_category: str = "to-be"
    diagram_notes: str = ""

    # OpenAI
    ai_prompt: str = ""
    is_loading: bool = False

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
            self.projects = session.exec(Project.select()).all()

    def add_project(self):
        if not self.project_name:
            return rx.window_alert("Project name is required")
        with rx.session() as session:
            project = Project(
                name=self.project_name, description=self.project_description
            )
            session.add(project)
            session.commit()
            session.refresh(project)
            self.load_projects()
            self.project_name = ""
            self.project_description = ""

    def select_project(self, project: Project):
        self.current_project = project
        self.load_diagrams()

    def load_diagrams(self):
        if not self.current_project:
            return
        with rx.session() as session:
            self.diagrams = session.exec(
                Diagram.select().where(Diagram.project_id == self.current_project.id)
            ).all()

    def add_diagram(self):
        if not self.current_project:
            return
        with rx.session() as session:
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

    def select_diagram(self, diagram: Diagram):
        self.current_diagram = diagram
        self.diagram_name = diagram.name
        self.diagram_content = diagram.content
        self.diagram_type = diagram.diagram_type
        self.diagram_category = diagram.category
        self.diagram_notes = diagram.notes

    def save_diagram(self):
        if not self.current_diagram:
            return
        with rx.session() as session:
            diagram = session.exec(
                Diagram.select().where(Diagram.id == self.current_diagram.id)
            ).first()
            diagram.name = self.diagram_name
            diagram.content = self.diagram_content
            diagram.diagram_type = self.diagram_type
            diagram.category = self.diagram_category
            diagram.notes = self.diagram_notes
            diagram.updated_at = datetime.now()
            session.add(diagram)
            session.commit()
            self.load_diagrams()

    async def generate_diagram(self):
        if not self.ai_prompt:
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
                        "content": f"Generate {self.diagram_type} code for the following requirement. Only return the code block without backticks if it is for PlantUML, or with backticks if it is for Mermaid.",
                    },
                    {"role": "user", "content": self.ai_prompt},
                ],
            )
            content = response.choices[0].message.content
            # Clean up content if it has backticks
            if content.startswith("```"):
                content = "\n".join(content.split("\n")[1:-1])
            self.diagram_content = content
        except Exception as e:
            yield rx.window_alert(f"Error generating diagram: {str(e)}")
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
            yield rx.window_alert(f"Error generating notes: {str(e)}")
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
