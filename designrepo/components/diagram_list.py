import reflex as rx
from ..state import State


def diagram_list():
    return rx.vstack(
        rx.flex(
            rx.heading("Diagrams", size="4", weight="bold"),
            rx.spacer(),
            rx.dialog.root(
                rx.dialog.trigger(
                    rx.icon_button(
                        rx.icon("plus"),
                        variant="ghost",
                        size="2",
                    ),
                ),
                rx.dialog.content(
                    rx.dialog.title("New Diagram"),
                    rx.dialog.description(
                        "Enter the name for the new diagram.",
                        size="2",
                        margin_bottom="4",
                    ),
                    rx.vstack(
                        rx.text(
                            "Diagram Name",
                            size="2",
                            weight="medium",
                        ),
                        rx.input(
                            placeholder="Enter diagram name",
                            value=State.diagram_name,
                            on_change=State.set_diagram_name,
                            variant="surface",
                            width="100%",
                        ),
                        rx.flex(
                            rx.dialog.close(
                                rx.button(
                                    "Cancel",
                                    variant="soft",
                                    color_scheme="gray",
                                ),
                            ),
                            rx.spacer(),
                            rx.button(
                                "Add Diagram",
                                on_click=State.add_diagram,
                                variant="solid",
                            ),
                            width="100%",
                            padding_top="4",
                        ),
                        width="100%",
                        spacing="3",
                    ),
                ),
                open=State.show_diagram_modal,
                on_open_change=State.set_show_diagram_modal,
            ),
            width="100%",
            align_items="center",
            padding_bottom="4",
        ),
        rx.divider(),
        rx.vstack(
            rx.foreach(
                State.diagrams,
                lambda diagram: rx.box(
                    rx.hstack(
                        rx.text(diagram.name, size="2", weight="medium"),
                        rx.spacer(),
                        rx.badge(
                            diagram.category,
                            color_scheme=rx.cond(
                                diagram.category == "to-be", "green", "orange"
                            ),
                            variant="surface",
                            size="1",
                        ),
                        width="100%",
                        align_items="center",
                        spacing="3",
                    ),
                    on_click=lambda: State.select_diagram(diagram),
                    background_color=rx.cond(
                        State.current_diagram.name == diagram.name,
                        rx.color("indigo", 3),
                        "transparent",
                    ),
                    color=rx.cond(
                        State.current_diagram.name == diagram.name,
                        rx.color("indigo", 9),
                        rx.color("gray", 11),
                    ),
                    border_radius="md",
                    cursor="pointer",
                    _hover={
                        "background_color": rx.cond(
                            State.current_diagram.name == diagram.name,
                            rx.color("indigo", 4),
                            rx.color("gray", 3),
                        ),
                    },
                    width="100%",
                    padding="10pt",
                ),
            ),
            width="100%",
            spacing="2",
            padding_top="4",
            padding_bottom="4",
        ),
        width="100%",
        align_items="start",
    )
