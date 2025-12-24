import reflex as rx
from ..state import State


def project_list():
    return rx.vstack(
        rx.flex(
            rx.heading("Projects", size="6", weight="bold"),
            rx.spacer(),
            rx.icon_button(
                rx.icon("plus"),
                variant="ghost",
                size="2",
            ),
            width="100%",
            align_items="center",
            padding_bottom="6",
        ),
        rx.divider(),
        rx.vstack(
            rx.foreach(
                State.projects,
                lambda project: rx.box(
                    rx.hstack(
                        rx.icon("folder", size=16),
                        rx.text(project.name),
                        width="100%",
                        align_items="center",
                        spacing="3",
                    ),
                    on_click=lambda: State.select_project(project),
                    background_color=rx.cond(
                        State.current_project.name == project.name,
                        rx.color("indigo", 3),
                        "transparent",
                    ),
                    color=rx.cond(
                        State.current_project.name == project.name,
                        rx.color("indigo", 9),
                        rx.color("gray", 11),
                    ),
                    border_radius="md",
                    cursor="pointer",
                    _hover={
                        "background_color": rx.cond(
                            State.current_project.name == project.name,
                            rx.color("indigo", 4),
                            rx.color("gray", 3),
                        ),
                    },
                    width="100%",
                    padding="5pt",
                ),
            ),
            width="100%",
            spacing="2",
            padding_top="6",
            padding_bottom="6",
        ),
        rx.spacer(),
        rx.divider(),
        rx.vstack(
            rx.text(
                "Create New Project", size="2", weight="medium", color_scheme="gray"
            ),
            rx.input(
                placeholder="Project Name",
                value=State.project_name,
                on_change=State.set_project_name,
                variant="surface",
                width="100%",
            ),
            rx.input(
                placeholder="Description",
                value=State.project_description,
                on_change=State.set_project_description,
                variant="surface",
                width="100%",
            ),
            rx.button(
                "Add Project",
                on_click=State.add_project,
                width="100%",
                variant="solid",
                margin_top="2",
            ),
            width="100%",
            spacing="4",
            padding_top="6",
        ),
        width="100%",
        padding="8",
        height="100vh",
        align_items="start",
    )
