from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from api.config import AppConfig, load_config
from api.neo4j_client import Neo4jClient
from api.repository import GraphRepository
from api.resolvers import ResolversBundle, build_resolvers_bundle


@dataclass(frozen=True)
class AppState:
    config: AppConfig
    neo4j_client: Neo4jClient
    repository: GraphRepository
    resolvers: ResolversBundle


def build_state(config: Optional[AppConfig] = None) -> AppState:
    cfg = config if config is not None else load_config()
    neo4j_client = Neo4jClient(cfg.neo4j)
    repository = GraphRepository(neo4j_client, cfg.graphql)
    resolvers = build_resolvers_bundle(cfg)
    return AppState(
        config=cfg,
        neo4j_client=neo4j_client,
        repository=repository,
        resolvers=resolvers,
    )
