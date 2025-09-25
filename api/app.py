from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List

from ariadne import format_error as ariadne_format_error
from ariadne.asgi import GraphQL
from fastapi import FastAPI, Request

from api.config import AppConfig, load_config
from api.errors import StructuredError, ValidationError
from api.neo4j_client import Neo4jClient
from api.repository import GraphRepository
from api.resolvers import ResolversBundle, build_resolvers_bundle
from api.validation import depth_limit_rule_factory


@dataclass(frozen=True)
class AppState:
    config: AppConfig
    neo4j_client: Neo4jClient
    repository: GraphRepository
    resolvers: ResolversBundle


def _build_error_formatter() -> Callable[[Any, bool], Dict[str, Any]]:
    def formatter(
        error: Any, debug: bool
    ) -> Dict[str, Any]:  # pragma: no cover - GraphQL runtime callback
        formatted = ariadne_format_error(error, debug)
        original = getattr(error, "original_error", None)

        if isinstance(original, StructuredError):
            payload = original.to_payload()
        else:
            hint = "Check available fields via GraphQL introspection"
            payload = {
                "type": "ValidationError"
                if not original
                else original.__class__.__name__,
                "message": error.message,
                "hint": hint,
            }
            if original and not isinstance(original, ValidationError):
                payload["type"] = original.__class__.__name__

        locations = error.locations or []
        if locations:
            loc = locations[0]
            payload["location"] = {"line": loc.line, "column": loc.column}

        formatted.setdefault("extensions", {})
        formatted["extensions"]["error"] = payload
        formatted["error"] = payload
        return formatted

    return formatter


def _create_graphql_app(state: AppState) -> GraphQL:
    validation_rules: List[Any] = [
        depth_limit_rule_factory(state.config.graphql.max_depth)
    ]

    def context_factory(request: Request) -> Dict[str, Any]:
        return {
            "request": request,
            "repo": state.repository,
            "config": state.config,
        }

    graphql_app = GraphQL(
        schema=state.resolvers.executable_schema,
        context_value=context_factory,
        debug=False,
        validation_rules=validation_rules,
        error_formatter=_build_error_formatter(),
    )
    return graphql_app


def create_app() -> FastAPI:
    config = load_config()
    neo4j_client = Neo4jClient(config.neo4j)
    repository = GraphRepository(neo4j_client, config.graphql)
    resolvers = build_resolvers_bundle(config)
    state = AppState(
        config=config,
        neo4j_client=neo4j_client,
        repository=repository,
        resolvers=resolvers,
    )

    app = FastAPI()
    app.state.graph_state = state

    graphql_app = _create_graphql_app(state)
    app.mount("/graphql", graphql_app)

    @app.on_event("shutdown")
    async def shutdown_event() -> None:  # pragma: no cover - lifecycle hook
        state.neo4j_client.close()

    @app.get("/healthz")
    async def healthcheck() -> Dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
