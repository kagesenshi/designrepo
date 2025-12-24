import reflex as rx
from ..state import State


def diagram_list():
    return rx.vstack(
        rx.heading("Diagrams", size="5"),
        rx.divider(),
        rx.vstack(
            rx.foreach(
                State.diagrams,
                lambda diagram: rx.button(
                    rx.hstack(
                        rx.text(diagram.name),
                        rx.badge(
                            diagram.category,
                            color_scheme=rx.cond(
                                diagram.category == "to-be", "green", "orange"
                            ),
                        ),
                        justify="between",
                        width="100%",
                    ),
                    on_click=lambda: State.select_diagram(diagram),
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
                placeholder="New Diagram Name",
                value=State.diagram_name,
                on_change=State.set_diagram_name,
            ),
            rx.button("Add Diagram", on_click=State.add_diagram, width="100%"),
            width="100%",
            spacing="2",
        ),
        width="100%",
        padding="2",
    )
