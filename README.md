# code-graph-mcp

Graph Model Context Protocol (MCP) backend exposing ontology-aligned graph data gathered in `../devtool-kg/` via a GraphQL API backed by Neo4j.

## Overview

- Ontology definitions mirror `devtool-kg/ontology.md`, and are codified in `src/code_graph_mcp/ontology.py`.
- GraphQL schema is generated programmatically from the ontology in `src/code_graph_mcp/schema_builder.py`, ensuring entity/relationship parity and typed traversals.
- Neo4j serves as the storage layer. Access is encapsulated by `src/code_graph_mcp/neo4j_client.py` and `src/code_graph_mcp/repository.py`.
- FastAPI + Ariadne expose the `/graphql` endpoint via `src/code_graph_mcp/app.py`.

## Local development

### Neo4j (Docker)

1. Create directories to persist Neo4j data and logs:

   ```bash
   mkdir -p neo4j/data neo4j/logs
   ```

2. Start Neo4j with Docker (includes basic APOC support and persistence):

   ```bash
   docker run \
     --name neo4j-code-graph \
     -p 7474:7474 \
     -p 7687:7687 \
     -e NEO4J_AUTH=neo4j/your_password \
     -e NEO4J_dbms_security_procedures_unrestricted=apoc.* \
     -e NEO4JLABS_PLUGINS='["apoc"]' \
     -v "$(pwd)/neo4j/data:/data" \
     -v "$(pwd)/neo4j/logs:/logs" \
     neo4j:5.22
   ```

3. Optional: add an index for faster lookups once the container is running:

   ```cypher
   CREATE CONSTRAINT entity_id IF NOT EXISTS
   FOR (n:Entity)
   REQUIRE n.id IS UNIQUE;
   ```

### Environment variables

Set the following values locally (e.g., in `.env` or Vercel settings):

- `CODE_GRAPH_NEO4J_URI` (example: `bolt://localhost:7687`)
- `CODE_GRAPH_NEO4J_USER` (example: `neo4j`)
- `CODE_GRAPH_NEO4J_PASSWORD` (example: `your_password`)
- `CODE_GRAPH_NEO4J_DATABASE` (default `neo4j`)
- Optional overrides: `CODE_GRAPH_FETCH_TIMEOUT_S`, `CODE_GRAPH_MAX_QUERY_DEPTH`, `CODE_GRAPH_DEFAULT_LIMIT`, `CODE_GRAPH_MAX_LIMIT`

### Vercel deployment notes

- `requirements.txt` lists all Python dependencies required by Vercel.
- `api/index.py` bootstraps the ASGI app, adding both the project root and `src/` to `sys.path` before importing `code_graph_mcp.main`.
- `vercel.json` routes `/graphql` and all other paths to the Python handler. Make sure `code_graph_mcp_config.yaml` is committed and available at the repository root.
- Supply the Neo4j environment variables through the Vercel dashboard. The service will fail with `ModuleNotFoundError` or connection errors if they are missing or incorrect.

## Schema & Introspection

`build_schema_sdl()` compiles the schema dynamically:

- Every ontology entity type becomes a GraphQL object implementing the `Entity` interface.
- Relation target unions are auto-generated where multiple entity types are valid.
- `EntityType` and `RelationType` enums align with ontology enumerations, enabling introspection-driven discovery.

You can inspect the schema using introspection queries or `GraphQL` Playground documentation explorer.

## Query Safety & Validation

Safeguards implemented across the stack include:

- **Depth Limiting:** `DepthLimitRule` in `src/code_graph_mcp/validation.py` enforces configurable maximum GraphQL query depth.
- **Pagination Caps:** `GraphQLConfig` limits per-query `limit` values (`QueryLimitError` is raised on violations).
- **Offset/Limit Validation:** Negative values raise `ValidationError` before hitting Neo4j.
- **Relation Constraints:** `GraphRepository.fetch_relation_targets()` only uses enumerated relation types mapped via `relation_to_neo4j_label()`.
- **Neo4j Error Wrapping:** Failures are wrapped in `InternalServerError` with hints for easier debugging.

## Structured Error Responses

Errors are emitted in a machine-readable format. Example response payload:

```json
{
  "errors": [
    {
      "message": "Requested limit 500 exceeds max 100",
      "extensions": {
        "error": {
          "type": "QueryLimitError",
          "message": "Requested limit 500 exceeds max 100",
          "details": {
            "max_limit": 100,
            "requested": 500
          }
        }
      },
      "error": {
        "type": "QueryLimitError",
        "message": "Requested limit 500 exceeds max 100",
        "details": {
          "max_limit": 100,
          "requested": 500
        }
      }
    }
  ]
}
```

GraphQL validation errors also include a `location` object when available.

## Access Control

The MCP currently allows unrestricted read queries against the graph. Introduce authentication middleware on FastAPI or enforce field-level authorization in resolvers if future scoping is required.

## Operational Considerations

- **Indexing:** Ensure Neo4j has indexes on `:Entity(id)` and `:Entity(type)` for prompt lookups (`id` field is used in graph matching).
- **Timeouts:** `CODE_GRAPH_FETCH_TIMEOUT_S` controls Neo4j transaction timeout to prevent runaway queries.
- **Caching:** Responses can be cached upstream (e.g., via CDN) if consistent snapshots are acceptable.
- **Schema Drift:** Regenerate the service whenever `devtool-kg/ontology.md` changes so GraphQL stays synchronized. Schema generation ties directly to ontology enumerations, minimizing manual edits.
- **Overfetch Mitigation:** Combine depth limit with the existing `limit` and `offset` controls to keep responses bounded. Additional cost analysis can be integrated into the repository layer if needed.

## Health Endpoint

`GET /healthz` returns `{ "status": "ok" }` for liveness checks.

## Project Layout

- `src/code_graph_mcp/ontology.py` — ontology enums & helper utilities.
- `src/code_graph_mcp/schema_builder.py` — dynamic GraphQL schema construction.
- `src/code_graph_mcp/repository.py` — Neo4j data access layer.
- `src/code_graph_mcp/resolvers.py` — Ariadne resolvers & limit enforcement.
- `src/code_graph_mcp/validation.py` — depth limiter rule.
- `src/code_graph_mcp/errors.py` — structured error classes.
- `src/code_graph_mcp/app.py` — FastAPI application wiring.
- `src/main.py` — entrypoint for ASGI servers.
