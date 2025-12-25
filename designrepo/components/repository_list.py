import reflex as rx
from ..state import State


def repository_list():
    return rx.vstack(
        rx.flex(
            rx.heading("Repositories", size="6", weight="bold"),
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
                    rx.dialog.title("Create New Repository"),
                    rx.dialog.description(
                        "Fill in the details to create a new repository.",
                        size="2",
                        margin_bottom="4",
                    ),
                    rx.vstack(
                        rx.text(
                            "Repository Name",
                            size="2",
                            weight="medium",
                        ),
                        rx.input(
                            placeholder="Enter repository name",
                            value=State.new_repository_name,
                            on_change=State.set_new_repository_name,
                            variant="surface",
                            width="100%",
                        ),
                        rx.text(
                            "Description",
                            size="2",
                            weight="medium",
                        ),
                        rx.input(
                            placeholder="Enter description",
                            value=State.new_repository_description,
                            on_change=State.set_new_repository_description,
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
                                "Add Repository",
                                on_click=State.add_repository,
                                variant="solid",
                            ),
                            width="100%",
                            padding_top="4",
                        ),
                        width="100%",
                        spacing="3",
                    ),
                ),
                open=State.show_repository_modal,
                on_open_change=State.set_show_repository_modal,
            ),
            width="100%",
            align_items="center",
            padding_bottom="6",
        ),
        rx.divider(),
        rx.vstack(
            rx.foreach(
                State.repositories,
                lambda repository: rx.box(
                    rx.hstack(
                        rx.icon("folder", size=16),
                        rx.text(repository.name),
                        rx.spacer(),
                        rx.hstack(
                            rx.icon_button(
                                rx.icon("chevron-up"),
                                size="1",
                                variant="ghost",
                                on_click=State.move_repository_up(
                                    repository.id
                                ).stop_propagation,
                            ),
                            rx.icon_button(
                                rx.icon("chevron-down"),
                                size="1",
                                variant="ghost",
                                on_click=State.move_repository_down(
                                    repository.id
                                ).stop_propagation,
                            ),
                            spacing="1",
                        ),
                        width="100%",
                        align_items="center",
                        spacing="3",
                    ),
                    on_click=lambda: State.select_repository(repository),
                    background_color=rx.cond(
                        State.current_repository.name == repository.name,
                        rx.color("indigo", 3),
                        "transparent",
                    ),
                    color=rx.cond(
                        State.current_repository.name == repository.name,
                        rx.color("indigo", 9),
                        rx.color("gray", 11),
                    ),
                    border_radius="md",
                    cursor="pointer",
                    _hover={
                        "background_color": rx.cond(
                            State.current_repository.name == repository.name,
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
        width="100%",
        padding="8",
        height="100vh",
        align_items="start",
    )
