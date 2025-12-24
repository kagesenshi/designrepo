import reflex as rx
from .state import State
from .components.project_list import project_list
from .components.diagram_list import diagram_list
from .components.diagram_editor import diagram_editor
from .components.preview import preview


def index() -> rx.Component:
    return rx.flex(
        rx.box(
            project_list(),
            width={"sm": "100%", "md": "280px", "lg": "320px"},
            height="100vh",
            border_right=f"1px solid {rx.color('gray', 4)}",
            background_color=rx.color("gray", 2),
            padding="10pt",
        ),
        rx.box(
            rx.cond(
                State.current_project,
                rx.vstack(
                    rx.flex(
                        rx.vstack(
                            rx.heading(
                                State.current_project.name, size="8", weight="bold"
                            ),
                            rx.text(
                                State.current_project.description,
                                color_scheme="gray",
                                size="2",
                            ),
                            align_items="start",
                            spacing="1",
                            padding_x="10pt",
                            padding_y="5pt",
                        ),
                        rx.spacer(),
                        rx.button(
                            rx.icon("refresh-cw"),
                            "Refresh Projects",
                            on_click=State.load_projects,
                            variant="soft",
                            size="2",
                        ),
                        width="100%",
                        align_items="center",
                        padding_bottom="8",
                    ),
                    rx.divider(),
                    rx.flex(
                        rx.box(
                            diagram_list(),
                            width={"sm": "100%", "md": "250px"},
                        ),
                        rx.box(
                            rx.cond(
                                State.current_diagram,
                                rx.flex(
                                    rx.box(
                                        diagram_editor(),
                                        flex="1",
                                        padding_right="2",
                                    ),
                                    rx.box(
                                        preview(),
                                        flex="1",
                                        padding_left="2",
                                    ),
                                    width="100%",
                                    direction={"sm": "column", "md": "row"},
                                    spacing="6",
                                ),
                                rx.center(
                                    rx.vstack(
                                        rx.icon(
                                            "layout_dashboard",
                                            size=40,
                                            color=rx.color("gray", 8),
                                        ),
                                        rx.text(
                                            "Select or add a diagram to start editing",
                                            color_scheme="gray",
                                        ),
                                        height="60vh",
                                        width="100%",
                                        justify="center",
                                    ),
                                    width="100%",
                                ),
                            ),
                            flex="1",
                        ),
                        width="100%",
                        padding_top="8",
                        direction={"sm": "column", "md": "row"},
                        spacing="5",
                        padding="10pt",
                    ),
                    width="100%",
                    padding="10",
                ),
                rx.center(
                    rx.vstack(
                        rx.heading("Requirement Management", size="9", weight="bold"),
                        rx.text(
                            "Select a project from the sidebar to manage diagrams and requirements.",
                            size="4",
                            color_scheme="gray",
                        ),
                        rx.button(
                            "Get Started",
                            on_click=State.load_projects,
                            size="3",
                            variant="solid",
                        ),
                        spacing="6",
                        text_align="center",
                    ),
                    width="100%",
                    height="100vh",
                ),
            ),
            flex="1",
            height="100vh",
            overflow_y="auto",
            background_color=rx.color("gray", 1),
        ),
        width="100%",
        direction="row",
    )


app = rx.App(
    theme=rx.theme(
        appearance="light",
        has_background=True,
        accent_color="indigo",
        radius="medium",
    ),
)
app.add_page(index, on_load=State.load_projects)
