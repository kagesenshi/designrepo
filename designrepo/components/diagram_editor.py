import reflex as rx
from ..state import State


def diagram_editor():
    return rx.card(
        rx.vstack(
            rx.flex(
                rx.heading("Diagram Editor", size="5", weight="bold"),
                rx.spacer(),
                rx.badge(State.diagram_type, variant="surface", color_scheme="indigo"),
                width="100%",
                align_items="center",
                padding_bottom="6",
            ),
            rx.divider(),
            rx.grid(
                rx.vstack(
                    rx.text("Name", size="2", weight="medium", color_scheme="gray"),
                    rx.input(
                        value=State.diagram_name,
                        on_change=State.set_diagram_name,
                        placeholder="Diagram name",
                        variant="surface",
                        width="100%",
                    ),
                    align_items="start",
                    spacing="2",
                ),
                rx.vstack(
                    rx.text("Type", size="2", weight="medium", color_scheme="gray"),
                    rx.select(
                        ["plantuml", "mermaid", "drawio"],
                        value=State.diagram_type,
                        on_change=State.set_diagram_type,
                        variant="surface",
                        width="100%",
                    ),
                    align_items="start",
                    spacing="2",
                ),
                rx.vstack(
                    rx.text("Category", size="2", weight="medium", color_scheme="gray"),
                    rx.select(
                        ["as-is", "to-be"],
                        value=State.diagram_category,
                        on_change=State.set_diagram_category,
                        variant="surface",
                        width="100%",
                    ),
                    align_items="start",
                    spacing="2",
                ),
                columns="3",
                spacing="6",
                width="100%",
                padding_top="6",
                padding_bottom="6",
            ),
            rx.cond(
                State.diagram_type == "drawio",
                rx.vstack(
                    rx.upload(
                        rx.vstack(
                            rx.icon("upload", size=24, color=rx.color("indigo", 9)),
                            rx.text(
                                "Drag and drop Draw.io file here or click to select",
                                size="2",
                            ),
                            align_items="center",
                            spacing="3",
                        ),
                        id="drawio_upload",
                        border=f"1px dashed {rx.color('gray', 5)}",
                        padding="8",
                        border_radius="md",
                        width="100%",
                        background_color=rx.color("gray", 2),
                    ),
                    rx.button(
                        "Upload Draw.io",
                        on_click=State.handle_upload(
                            rx.upload_files(upload_id="drawio_upload")
                        ),
                        width="100%",
                        variant="soft",
                        size="2",
                    ),
                    width="100%",
                    spacing="4",
                ),
                rx.vstack(
                    rx.text("Content", size="2", weight="medium", color_scheme="gray"),
                    rx.text_area(
                        value=State.diagram_content,
                        on_change=State.set_diagram_content,
                        placeholder="Enter diagram code here...",
                        height="400px",
                        width="100%",
                        variant="surface",
                        style={
                            "font-family": "monospace",
                            "font-size": "13px",
                            "padding": "12px",
                        },
                    ),
                    width="100%",
                    spacing="2",
                ),
            ),
            rx.divider(),
            rx.vstack(
                rx.flex(
                    rx.hstack(
                        rx.icon("sparkles", size=18, color=rx.color("amber", 9)),
                        rx.heading("AI Assistant", size="3", weight="bold"),
                        align_items="center",
                        spacing="2",
                    ),
                    width="100%",
                    padding_top="6",
                ),
                rx.flex(
                    rx.input(
                        value=State.ai_prompt,
                        on_change=State.set_ai_prompt,
                        placeholder="Ask AI to generate diagram code or notes...",
                        variant="surface",
                        flex="1",
                    ),
                    rx.button(
                        "Generate",
                        on_click=State.generate_diagram,
                        is_loading=State.is_loading,
                        variant="soft",
                        padding_x="6",
                    ),
                    spacing="3",
                    width="100%",
                ),
                spacing="4",
                width="100%",
            ),
            rx.divider(),
            rx.vstack(
                rx.text(
                    "Notes (Markdown)", size="2", weight="medium", color_scheme="gray"
                ),
                rx.text_area(
                    value=State.diagram_notes,
                    on_change=State.set_diagram_notes,
                    placeholder="Enter notes in markdown...",
                    height="250px",
                    width="100%",
                    variant="surface",
                    style={"padding": "12px"},
                ),
                width="100%",
                spacing="2",
                padding_top="4",
            ),
            rx.button(
                rx.icon("save"),
                "Save Changes",
                on_click=State.save_diagram,
                width="100%",
                size="3",
                variant="solid",
                margin_top="4",
            ),
            width="100%",
            spacing="6",
        ),
        width="100%",
        padding="8",
    )
