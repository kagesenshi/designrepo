import reflex as rx
from ..state import State


def diagram_editor():
    return rx.vstack(
        rx.heading("Diagram Editor", size="6"),
        rx.hstack(
            rx.vstack(
                rx.text("Name"),
                rx.input(
                    value=State.diagram_name,
                    on_change=State.set_diagram_name,
                    placeholder="Diagram name",
                ),
                align_items="start",
            ),
            rx.vstack(
                rx.text("Type"),
                rx.select(
                    ["plantuml", "mermaid", "drawio"],
                    value=State.diagram_type,
                    on_change=State.set_diagram_type,
                ),
                align_items="start",
            ),
            rx.vstack(
                rx.text("Category"),
                rx.select(
                    ["as-is", "to-be"],
                    value=State.diagram_category,
                    on_change=State.set_diagram_category,
                ),
                align_items="start",
            ),
            width="100%",
            justify="between",
        ),
        rx.cond(
            State.diagram_type == "drawio",
            rx.vstack(
                rx.upload(
                    rx.vstack(
                        rx.button(
                            "Select File", color_scheme="blue", variant="surface"
                        ),
                        rx.text("Drag and drop Draw.io file here or click to select"),
                    ),
                    id="drawio_upload",
                    border="2px dashed #e0e0e0",
                    padding="4",
                    width="100%",
                ),
                rx.button(
                    "Upload Draw.io File",
                    on_click=State.handle_upload(
                        rx.upload_files(upload_id="drawio_upload")
                    ),
                    width="100%",
                ),
                width="100%",
            ),
            rx.vstack(
                rx.text("Content"),
                rx.text_area(
                    value=State.diagram_content,
                    on_change=State.set_diagram_content,
                    placeholder="Enter diagram code here...",
                    height="300px",
                    width="100%",
                ),
                width="100%",
            ),
        ),
        rx.divider(),
        rx.heading("AI Assistant", size="4"),
        rx.hstack(
            rx.input(
                value=State.ai_prompt,
                on_change=State.set_ai_prompt,
                placeholder="Ask AI to generate diagram code or notes...",
                width="100%",
            ),
            rx.button(
                "Generate Diagram",
                on_click=State.generate_diagram,
                is_loading=State.is_loading,
            ),
            rx.button(
                "Generate Notes",
                on_click=State.generate_notes,
                is_loading=State.is_loading,
            ),
            width="100%",
        ),
        rx.divider(),
        rx.text("Notes (Markdown)"),
        rx.text_area(
            value=State.diagram_notes,
            on_change=State.set_diagram_notes,
            placeholder="Enter notes in markdown...",
            height="200px",
            width="100%",
        ),
        rx.button(
            "Save Diagram",
            on_click=State.save_diagram,
            color_scheme="blue",
            width="100%",
        ),
        width="100%",
        spacing="4",
        padding="4",
        border="1px solid #e0e0e0",
        border_radius="lg",
    )
