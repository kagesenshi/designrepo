import reflex as rx
from ..state import State


def project_list():
    return rx.vstack(
        rx.heading("Projects", size="6"),
        rx.divider(),
        rx.button(
            "Load Projects",
            on_click=State.load_projects,
            size="2",
        ),
        rx.vstack(
            rx.foreach(
                State.projects,
                lambda project: rx.button(
                    project.name,
                    on_click=lambda: State.select_project(project),
                    variant="ghost",
                    width="100%",
                ),
            ),
            width="100%",
            spacing="2",
        ),
        rx.divider(),
        rx.vstack(
            rx.input(
                placeholder="New Project Name",
                value=State.project_name,
                on_change=State.set_project_name,
            ),
            rx.input(
                placeholder="Description",
                value=State.project_description,
                on_change=State.set_project_description,
            ),
            rx.button("Add Project", on_click=State.add_project, width="100%"),
            width="100%",
            spacing="2",
        ),
        width="20%",
        padding="4",
        background_color="#f9f9f9",
        height="100vh",
    )
