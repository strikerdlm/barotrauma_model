"""
api
===

FastAPI sidecar wrapping ``barotrauma.v2.simulate`` for the TypeScript
frontend. Single source of truth: the Python physics engine stays
authoritative; the frontend never re-implements the model.

Run locally:
    uvicorn api.main:app --reload --port 8000

The Vite dev server (``frontend/``) proxies ``/api/*`` to
``http://localhost:8000`` — see ``frontend/vite.config.ts``.
"""
