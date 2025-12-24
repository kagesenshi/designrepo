import reflex as rx

config = rx.Config(
    app_name="designrepo",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)