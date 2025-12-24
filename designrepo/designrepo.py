import reflex as rx
from .state import State
from .components.project_list import project_list
from .components.diagram_list import diagram_list
from .components.diagram_editor import diagram_editor
from .components.preview import preview


def index() -> rx.Component:
    return rx.hstack(
        project_list(),
        rx.vstack(
            rx.cond(
                State.current_project,
                rx.vstack(
                    rx.heading(f"Project: {State.current_project.name}", size="7"),
                    rx.text(State.current_project.description),
                    rx.divider(),
                    rx.hstack(
                        rx.vstack(
                            diagram_list(),
                            width="250px",
                            border_right="1px solid #eee",
                        ),
                        rx.cond(
                            State.current_diagram,
                            rx.hstack(
                                rx.box(diagram_editor(), width="50%"),
                                rx.box(preview(), width="50%"),
                                width="100%",
                                align_items="start",
                            ),
                            rx.center(
                                rx.text("Select or add a diagram to start editing"),
                                width="100%",
                                height="80vh",
                            ),
                        ),
                        width="100%",
                        align_items="start",
                    ),
                    width="100%",
                    padding="4",
                ),
                rx.center(
                    rx.vstack(
                        rx.heading("Requirement Management Program", size="9"),
                        rx.text(
                            "Select a project from the sidebar to get started", size="5"
                        ),
                        rx.button("Refresh Projects", on_click=State.load_projects),
                        spacing="5",
                    ),
                    width="100%",
                    height="100vh",
                ),
            ),
            width="80%",
            height="100vh",
            overflow_y="auto",
        ),
        width="100%",
        spacing="0",
    )


app = rx.App(
    theme=rx.theme(
        appearance="light",
        has_background=True,
        accent_color="blue",
    ),
)
app.add_page(index, on_load=State.load_projects)
