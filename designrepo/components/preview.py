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
            rx.tabs.root(
                rx.tabs.list(
                    rx.tabs.trigger(
                        rx.hstack(rx.icon("image", size=14), rx.text("Diagram")),
                        value="diagram",
                    ),
                    rx.tabs.trigger(
                        rx.hstack(rx.icon("file-text", size=14), rx.text("Notes")),
                        value="notes",
                    ),
                    spacing="6",
                ),
                rx.tabs.content(
                    rx.vstack(
                        rx.box(
                            rx.cond(
                                State.diagram_type == "mermaid",
                                rx.image(
                                    src=State.mermaid_url,
                                    width="100%",
                                    border_radius="md",
                                ),
                                rx.cond(
                                    State.diagram_type == "plantuml",
                                    rx.image(
                                        src=State.plantuml_url,
                                        width="100%",
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
                            padding_top="8",
                            padding_bottom="4",
                        ),
                        width="100%",
                    ),
                    value="diagram",
                ),
                rx.tabs.content(
                    rx.box(
                        rx.markdown(State.diagram_notes),
                        width="100%",
                        padding="8",
                        background_color=rx.color("gray", 2),
                        border_radius="lg",
                        margin_top="8",
                    ),
                    value="notes",
                ),
                default_value="diagram",
                width="100%",
            ),
            width="100%",
            spacing="1",
        ),
        width="100%",
        padding="8",
    )
