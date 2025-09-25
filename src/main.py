from __future__ import annotations

from fastapi import FastAPI

from code_graph_mcp.app import create_app


def get_app() -> FastAPI:
    return create_app()


app = get_app()
