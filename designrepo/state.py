import reflex as rx
import hashlib
from typing import List, Optional
import openai
from datetime import datetime
import urllib.parse
import zlib
import base64
import pendulum
import pydantic
from .models import Repository, Diagram, User
import httpx
from authlib.integrations.httpx_client import AsyncOAuth2Client
from .settings import settings


class RepositorySchema(pydantic.BaseModel):
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    order_index: int = 0
    created_at: Optional[datetime] = None


class DiagramSchema(pydantic.BaseModel):
    id: Optional[int] = None
    repository_id: Optional[int] = None
    name: str = ""
    content: str = ""
    diagram_type: str = "plantuml"
    category: str = "to-be"
    notes: str = ""
    last_ai_prompt: str = ""
    last_ai_notes_prompt: str = ""
    order_index: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserSchema(pydantic.BaseModel):
    id: Optional[int] = None
    sub: str = ""
    email: str = ""
    name: str = ""
    picture: str = ""

    @pydantic.computed_field
    @property
    def gravatar_url(self) -> str:
        if not self.email:
            return ""
        email_hash = hashlib.md5(self.email.lower().strip().encode()).hexdigest()
        return f"https://www.gravatar.com/avatar/{email_hash}?d=identicon"


class State(rx.State):
    """The base state for the app."""

    state_auto_setters = False

    repositories: List[RepositorySchema] = []
    current_repository: Optional[RepositorySchema] = None

    diagrams: List[DiagramSchema] = []
    current_diagram: Optional[DiagramSchema] = None

    user: Optional[UserSchema] = None
    oidc_user_sub: str = rx.Cookie("", name="oidc_user_sub")
    oidc_state_cookie: str = rx.Cookie("", name="oidc_state")

    async def get_oidc_config(self):
        issuer = settings.oidc_issuer
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{issuer}/.well-known/openid-configuration")
            return resp.json()

    async def login(self):
        config = await self.get_oidc_config()
        client = AsyncOAuth2Client(
            client_id=settings.oidc_client_id,
            client_secret=settings.oidc_client_secret,
            scope="openid email profile",
            redirect_uri=settings.oidc_redirect_uri or self.router.url,
        )
        uri, state = client.create_authorization_url(config["authorization_endpoint"])
        self.oidc_state_cookie = state
        return rx.redirect(uri)

    async def handle_callback(self, code, state):
        if state != self.oidc_state_cookie:
            return rx.toast.error("Invalid OIDC state")

        config = await self.get_oidc_config()
        async with httpx.AsyncClient() as client:
            # Token exchange
            resp = await client.post(
                config["token_endpoint"],
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": settings.oidc_redirect_uri or self.router.url,
                    "client_id": settings.oidc_client_id,
                    "client_secret": settings.oidc_client_secret,
                },
            )
            token = resp.json()
            access_token = token.get("access_token")

            # User info
            resp = await client.get(
                config["userinfo_endpoint"],
                headers={"Authorization": f"Bearer {access_token}"},
            )
            user_info = resp.json()

            sub = user_info["sub"]
            email = user_info.get("email", "")
            name = user_info.get("name", "")
            picture = user_info.get("picture", "")

            with rx.session() as session:
                user = session.exec(User.select().where(User.sub == sub)).first()
                if not user:
                    user = User(sub=sub, email=email, name=name, picture=picture)
                    session.add(user)
                else:
                    user.email = email
                    user.name = name
                    user.picture = picture
                session.commit()

            self.oidc_user_sub = sub
            self.user = UserSchema(sub=sub, email=email, name=name, picture=picture)

    async def on_load(self):
        if not settings.oidc_issuer:
            self.user = UserSchema(
                sub="local",
                email="local@example.com",
                name="Local User",
            )
            await self.load_repositories()
            return

        code = self.router_data.get("query", {}).get("code")
        state = self.router_data.get("query", {}).get("state")

        if code:
            await self.handle_callback(code, state)
            return rx.redirect("/")

        if self.oidc_user_sub:
            with rx.session() as session:
                user = session.exec(
                    User.select().where(User.sub == self.oidc_user_sub)
                ).first()
                if user:
                    self.user = UserSchema(
                        id=user.id,
                        sub=user.sub,
                        email=user.email,
                        name=user.name,
                        picture=user.picture,
                    )
        await self.load_repositories()

    def logout(self):
        self.user = None
        self.oidc_user_sub = ""
        return rx.redirect("/")

    # Form fields
    repository_name: str = ""
    repository_description: str = ""

    diagram_name: str = ""
    diagram_content: str = ""
    diagram_type: str = "plantuml"
    diagram_category: str = "to-be"
    diagram_notes: str = ""

    # Creation form fields
    new_repository_name: str = ""
    new_repository_description: str = ""
    new_diagram_name: str = ""

    # Modal visibility
    show_repository_modal: bool = False
    show_diagram_modal: bool = False

    # OpenAI
    ai_prompt: str = ""
    ai_notes_prompt: str = ""
    is_loading: bool = False
    show_ai_modal: bool = False
    show_ai_notes_modal: bool = False
    refer_to_diagram: bool = True

    def toggle_ai_modal(self):
        self.show_ai_modal = not self.show_ai_modal

    def toggle_ai_notes_modal(self):
        self.show_ai_notes_modal = not self.show_ai_notes_modal

    def set_repository_name(self, value: str):
        self.repository_name = value

    def set_repository_description(self, value: str):
        self.repository_description = value

    def set_new_repository_name(self, value: str):
        self.new_repository_name = value

    def set_new_repository_description(self, value: str):
        self.new_repository_description = value

    def set_diagram_name(self, value: str):
        self.diagram_name = value

    def set_new_diagram_name(self, value: str):
        self.new_diagram_name = value

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

    def set_ai_notes_prompt(self, value: str):
        self.ai_notes_prompt = value

    def set_refer_to_diagram(self, value: bool):
        self.refer_to_diagram = value

    def set_show_repository_modal(self, value: bool):
        self.show_repository_modal = value
        if value:
            self.new_repository_name = ""
            self.new_repository_description = ""

    def set_show_diagram_modal(self, value: bool):
        self.show_diagram_modal = value
        if value:
            self.new_diagram_name = ""

    def set_show_ai_modal(self, value: bool):
        self.show_ai_modal = value

    def set_show_ai_notes_modal(self, value: bool):
        self.show_ai_notes_modal = value

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

    async def load_repositories(self):
        with rx.session() as session:
            db_repositories = session.exec(
                Repository.select().order_by(Repository.order_index)
            ).all()
            self.repositories = [
                RepositorySchema(
                    id=p.id,
                    name=p.name,
                    description=p.description,
                    order_index=p.order_index,
                    created_at=p.created_at,
                )
                for p in db_repositories
            ]

    async def add_repository(self):
        if not self.new_repository_name:
            return rx.toast.error("Repository name is required")
        with rx.session() as session:
            # Check for duplicate repository name
            existing = session.exec(
                Repository.select().where(Repository.name == self.new_repository_name)
            ).first()
            if existing:
                return rx.toast.error(
                    f"Repository '{self.new_repository_name}' already exists."
                )

            # Get max order_index
            max_order = session.exec(
                Repository.select().order_by(Repository.order_index.desc())
            ).first()
            new_order = (max_order.order_index + 1) if max_order else 0

            repository = Repository(
                name=self.new_repository_name,
                description=self.new_repository_description,
                order_index=new_order,
            )
            session.add(repository)
            session.commit()
            session.refresh(repository)
            await self.load_repositories()
            self.new_repository_name = ""
            self.new_repository_description = ""
            self.show_repository_modal = False

    async def select_repository(self, repository: RepositorySchema):
        self.current_repository = repository
        self.current_diagram = None
        await self.load_diagrams()

    async def load_diagrams(self):
        if not self.current_repository:
            return
        with rx.session() as session:
            db_diagrams = session.exec(
                Diagram.select()
                .where(Diagram.repository_id == self.current_repository.id)
                .order_by(Diagram.order_index)
            ).all()
            self.diagrams = [
                DiagramSchema(
                    id=d.id,
                    repository_id=d.repository_id,
                    name=d.name,
                    content=d.content,
                    diagram_type=d.diagram_type,
                    category=d.category,
                    notes=d.notes,
                    last_ai_prompt=d.last_ai_prompt,
                    last_ai_notes_prompt=d.last_ai_notes_prompt,
                    order_index=d.order_index,
                    created_at=d.created_at,
                    updated_at=d.updated_at,
                )
                for d in db_diagrams
            ]

    async def add_diagram(self):
        if not self.current_repository:
            return
        if not self.new_diagram_name:
            return rx.toast.error("Diagram name is required")

        with rx.session() as session:
            # Check for duplicate diagram name in the same repository
            existing = session.exec(
                Diagram.select().where(
                    (Diagram.repository_id == self.current_repository.id)
                    & (Diagram.name == self.new_diagram_name)
                )
            ).first()
            if existing:
                return rx.toast.error(
                    f"Diagram '{self.new_diagram_name}' already exists in this repository."
                )

            # Get max order_index for this repository
            max_order = session.exec(
                Diagram.select()
                .where(Diagram.repository_id == self.current_repository.id)
                .order_by(Diagram.order_index.desc())
            ).first()
            new_order = (max_order.order_index + 1) if max_order else 0

            diagram = Diagram(
                repository_id=self.current_repository.id,
                name=self.new_diagram_name,
                content="",  # Default empty
                diagram_type="plantuml",  # Default
                category="to-be",  # Default
                notes="",  # Default empty
                order_index=new_order,
            )
            session.add(diagram)
            session.commit()
            await self.load_diagrams()
            self.new_diagram_name = ""
            self.current_diagram = None
            self.show_diagram_modal = False

    is_editing: bool = False

    def set_is_editing(self, value: bool):
        self.is_editing = value

    def select_diagram(self, diagram: DiagramSchema):
        self.current_diagram = diagram
        self.diagram_name = diagram.name
        self.diagram_content = diagram.content
        self.diagram_type = diagram.diagram_type
        self.diagram_notes = diagram.notes
        self.ai_prompt = diagram.last_ai_prompt
        self.ai_notes_prompt = diagram.last_ai_notes_prompt

    def edit_diagram(self, diagram: DiagramSchema):
        self.select_diagram(diagram)
        self.is_editing = True

    def show_diagram(self, diagram: DiagramSchema):
        self.is_editing = False
        self.select_diagram(diagram)
        pass

    async def save_diagram(self):
        if not self.current_diagram:
            return
        if not self.diagram_name:
            return rx.toast.error("Diagram name is required")

        with rx.session() as session:
            # Check for duplicate diagram name (excluding the current one)
            existing = session.exec(
                Diagram.select().where(
                    (Diagram.repository_id == self.current_diagram.repository_id)
                    & (Diagram.name == self.diagram_name)
                    & (Diagram.id != self.current_diagram.id)
                )
            ).first()
            if existing:
                return rx.toast.error(
                    f"Another diagram named '{self.diagram_name}' already exists in this repository."
                )

            diagram = session.exec(
                Diagram.select().where(Diagram.id == self.current_diagram.id)
            ).first()
            diagram.name = self.diagram_name
            diagram.content = self.diagram_content
            diagram.diagram_type = self.diagram_type
            diagram.category = self.diagram_category
            diagram.notes = self.diagram_notes
            diagram.last_ai_prompt = self.ai_prompt
            diagram.last_ai_notes_prompt = self.ai_notes_prompt
            diagram.updated_at = datetime.now(tz=pendulum.local_timezone())
            session.add(diagram)
            session.commit()
            session.refresh(diagram)
            await self.load_diagrams()
            # Update current diagram in state to reflect changes
            self.current_diagram = DiagramSchema(
                id=diagram.id,
                repository_id=diagram.repository_id,
                name=diagram.name,
                content=diagram.content,
                diagram_type=diagram.diagram_type,
                category=diagram.category,
                notes=diagram.notes,
                last_ai_prompt=diagram.last_ai_prompt,
                last_ai_notes_prompt=diagram.last_ai_notes_prompt,
                created_at=diagram.created_at,
                updated_at=diagram.updated_at,
            )

            self.is_editing = False

    async def generate_diagram(self):
        if not self.ai_prompt:
            return
        self.is_loading = True
        self.show_ai_modal = False
        yield

        try:
            client = openai.AsyncOpenAI(api_key=settings.openai_api_key)

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
            # Prompt is preserved for next time as per user request
        except Exception as e:
            yield rx.toast.error(f"Error generating diagram: {str(e)}")
        finally:
            self.is_loading = False
            yield

    async def generate_notes(self):
        if not self.ai_notes_prompt:
            return
        self.is_loading = True
        self.show_ai_notes_modal = False
        yield

        try:
            client = openai.AsyncOpenAI(api_key=settings.openai_api_key)

            system_msg = (
                "Generate markdown documentation/notes based on the user instruction."
            )
            user_content = f"Instruction: {self.ai_notes_prompt}\n"

            if self.refer_to_diagram and self.diagram_content:
                user_content += f"\nRelevant Diagram Content ({self.diagram_type}):\n{self.diagram_content}"

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
            self.diagram_notes = response.choices[0].message.content
            # Prompt is preserved for next time as per user request
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

    async def move_repository_up(self, repo_id: int):
        with rx.session() as session:
            current = session.exec(
                Repository.select().where(Repository.id == repo_id)
            ).first()
            if not current:
                return

            # Find the item just before this one
            previous = session.exec(
                Repository.select()
                .where(Repository.order_index < current.order_index)
                .order_by(Repository.order_index.desc())
            ).first()

            if previous:
                # Swap order indices
                current.order_index, previous.order_index = (
                    previous.order_index,
                    current.order_index,
                )
                session.add(current)
                session.add(previous)
                session.commit()
                await self.load_repositories()

    async def move_repository_down(self, repo_id: int):
        with rx.session() as session:
            current = session.exec(
                Repository.select().where(Repository.id == repo_id)
            ).first()
            if not current:
                return

            # Find the item just after this one
            next_repo = session.exec(
                Repository.select()
                .where(Repository.order_index > current.order_index)
                .order_by(Repository.order_index.asc())
            ).first()

            if next_repo:
                # Swap order indices
                current.order_index, next_repo.order_index = (
                    next_repo.order_index,
                    current.order_index,
                )
                session.add(current)
                session.add(next_repo)
                session.commit()
                await self.load_repositories()

    async def move_diagram_up(self, diag_id: int):
        with rx.session() as session:
            current = session.exec(
                Diagram.select().where(Diagram.id == diag_id)
            ).first()
            if not current:
                return

            # Find the item just before this one in the same repository
            previous = session.exec(
                Diagram.select()
                .where(
                    (Diagram.repository_id == current.repository_id)
                    & (Diagram.order_index < current.order_index)
                )
                .order_by(Diagram.order_index.desc())
            ).first()

            if previous:
                # Swap order indices
                current.order_index, previous.order_index = (
                    previous.order_index,
                    current.order_index,
                )
                session.add(current)
                session.add(previous)
                session.commit()
                await self.load_diagrams()

    async def move_diagram_down(self, diag_id: int):
        with rx.session() as session:
            current = session.exec(
                Diagram.select().where(Diagram.id == diag_id)
            ).first()
            if not current:
                return

            # Find the item just after this one in the same repository
            next_diag = session.exec(
                Diagram.select()
                .where(
                    (Diagram.repository_id == current.repository_id)
                    & (Diagram.order_index > current.order_index)
                )
                .order_by(Diagram.order_index.asc())
            ).first()

            if next_diag:
                # Swap order indices
                current.order_index, next_diag.order_index = (
                    next_diag.order_index,
                    current.order_index,
                )
                session.add(current)
                session.add(next_diag)
                session.commit()
                await self.load_diagrams()
