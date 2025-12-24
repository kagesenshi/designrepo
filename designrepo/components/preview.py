import reflex as rx
from ..state import State
import base64
import zlib


def encode_plantuml(text: str) -> str:
    """Encode PlantUML text for the public renderer."""
    # Simplified version: many online renderers accept some form of encoding
    # For now, let's use a simple approach or just assume we can send it
    # Actually, PlantUML public server uses a specific encoding.
    # If I can't easily implement it here, I might just use a placeholder or
    # use a library if I can find one.
    # Let's try to implement the real one.
    try:
        zlibbed_str = zlib.compress(text.encode("utf-8"))
        compressed_string = zlibbed_str[2:-4]
        return (
            base64.b64encode(compressed_string)
            .decode("utf-8")
            .replace("+", "-")
            .replace("/", "_")
        )
    except:
        return ""


def preview():
    return rx.card(
        rx.vstack(
            rx.flex(
                rx.hstack(
                    rx.icon("eye", size=18, color=rx.color("gray", 9)),
                    rx.heading("Preview", size="5", weight="bold"),
                    align_items="center",
                    spacing="2",
                ),
                rx.spacer(),
                width="100%",
                padding_bottom="6",
            ),
            rx.divider(),
            # Diagram Section
            rx.box(
                rx.cond(
                    State.diagram_type == "mermaid",
                    rx.image(
                        src=State.mermaid_url,
                        border_radius="md",
                    ),
                    rx.cond(
                        State.diagram_type == "plantuml",
                        rx.image(
                            src=State.plantuml_url,
                            border_radius="md",
                        ),
                        rx.el.iframe(
                            src=State.drawio_url,
                            frameborder="0",
                            style={
                                "width": "100%",
                                "height": "650px",
                                "border-radius": "12px",
                                "background": "white",
                            },
                        ),
                    ),
                ),
                width="100%",
                padding_top="4",
                padding_bottom="4",
            ),
            rx.divider(),
            # Notes Section
            rx.vstack(
                rx.hstack(
                    rx.icon("file-text", size=18, color=rx.color("gray", 9)),
                    rx.heading("Notes", size="4", weight="bold"),
                    align_items="center",
                    spacing="2",
                    padding_top="4",
                ),
                rx.box(
                    rx.markdown(State.diagram_notes),
                    width="100%",
                    padding="8",
                    background_color=rx.color("gray", 2),
                    border_radius="lg",
                ),
                width="100%",
                spacing="4",
                align_items="start",
            ),
            width="100%",
            spacing="1",
        ),
        width="100%",
        padding="8",
    )
