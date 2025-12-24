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
    return rx.vstack(
        rx.heading("Preview", size="6"),
        rx.tabs.root(
            rx.tabs.list(
                rx.tabs.trigger("Diagram", value="diagram"),
                rx.tabs.trigger("Notes", value="notes"),
            ),
            rx.tabs.content(
                rx.vstack(
                    rx.cond(
                        State.diagram_type == "mermaid",
                        rx.image(src=State.mermaid_url),
                        rx.cond(
                            State.diagram_type == "plantuml",
                            rx.image(src=State.plantuml_url),
                            rx.el.iframe(
                                src=State.drawio_url,
                                frameborder="0",
                                style={"width": "100%", "height": "500px"},
                            ),
                        ),
                    )
                ),
                value="diagram",
            ),
            rx.tabs.content(
                rx.markdown(State.diagram_notes),
                value="notes",
            ),
            default_value="diagram",
            width="100%",
        ),
        width="100%",
        padding="4",
        border="1px solid #e0e0e0",
        border_radius="lg",
    )
