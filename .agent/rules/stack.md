---
trigger: always_on
---

This project following technologies:

* dependency management:  UV
* container engine: podman
* deployment system: kubernetes with argocd
* authentication: OIDC
* frontend framework: reflex.dev
* backend framework: fastapi
* database: postgresql
* i/o pattern: prefer asyncio

always use `uv run reflex` to run reflex