from __future__ import annotations

from fastmcp import FastMCP

from api.errors import QueryLimitError, ValidationError
from api.ontology import entity_type_from_enum, relation_type_from_enum
from api.state import AppState


def build_mcp_server(state: AppState, *, manage_lifespan: bool = True) -> FastMCP:
    mcp = FastMCP(
        name="Code Graph MCP",
        instructions=(
            "Graph-aware MCP server exposing documentation ontology entities "
            "and relations backed by Neo4j."
        ),
    )

    @mcp.tool
    async def fetch_entity(entity_id: str) -> dict | None:
        repo = state.repository
        return repo.fetch_entity(entity_id)

    @mcp.tool
    async def fetch_entities(
        type: str | None = None,
        search: str | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[dict]:
        repo = state.repository
        gql_conf = state.config.graphql
        effective_limit = limit if limit is not None else gql_conf.default_limit
        assert offset >= 0, "Offset must be non-negative"
        if effective_limit > gql_conf.max_limit:
            raise QueryLimitError(
                f"Requested limit {effective_limit} exceeds max {gql_conf.max_limit}",
                max_limit=gql_conf.max_limit,
                requested=effective_limit,
            )
        entity_type = None
        if type is not None:
            entity_type = entity_type_from_enum(type)
        return repo.fetch_entities(entity_type, search, effective_limit, offset)

    @mcp.tool
    async def fetch_relations(
        source_id: str,
        relation: str,
        direction: str = "OUTGOING",
        limit: int | None = None,
        offset: int = 0,
    ) -> list[dict]:
        repo = state.repository
        gql_conf = state.config.graphql
        effective_limit = limit if limit is not None else gql_conf.default_limit
        assert offset >= 0, "Offset must be non-negative"
        if effective_limit > gql_conf.max_limit:
            raise QueryLimitError(
                f"Requested limit {effective_limit} exceeds max {gql_conf.max_limit}",
                max_limit=gql_conf.max_limit,
                requested=effective_limit,
            )
        direction_value = direction.upper() if direction else "OUTGOING"
        if direction_value not in {"OUTGOING", "INCOMING"}:
            raise ValidationError(
                f"Unsupported relation direction '{direction}'. Use OUTGOING or INCOMING.",
                hint="Use RelationDirection enum values.",
            )
        relation_type = relation_type_from_enum(relation)
        return repo.fetch_relation_targets(
            source_id=source_id,
            relation_type=relation_type,
            direction=direction_value,
            limit=effective_limit,
            offset=offset,
        )

    if manage_lifespan:
        @mcp.lifespan
        async def lifespan(_: FastMCP):
            try:
                yield
            finally:
                state.neo4j_client.close()

    return mcp
