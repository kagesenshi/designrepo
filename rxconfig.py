import reflex as rx
from designrepo.settings import settings

config = rx.Config(
    app_name="designrepo",
    db_url=settings.db_url,
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ],
)
