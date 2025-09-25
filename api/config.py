from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv


CONFIG_FILENAME = "code_graph_mcp_config.yaml"
CONFIG_PATH = Path(__file__).resolve().parents[1] / CONFIG_FILENAME

load_dotenv()


@dataclass(frozen=True)
class Neo4jConfig:
    uri: str
    """Bolt URI for the Neo4j connection."""

    username: str
    """Neo4j username used for authentication."""

    password: str
    """Neo4j password resolved from environment variables."""

    database: Optional[str] = None
    """Optional Neo4j database name when using multi-database setups."""

    fetch_timeout_s: float = 5.0
    """Transaction timeout (seconds) applied to read queries."""


@dataclass(frozen=True)
class GraphQLConfig:
    max_depth: int
    """Maximum GraphQL query depth allowed by the validation rule."""

    default_limit: int
    """Default pagination limit applied when a query omits the argument."""

    max_limit: int
    """Upper bound on pagination limits accepted by the API."""


@dataclass(frozen=True)
class AppConfig:
    neo4j: Neo4jConfig
    """Neo4j connection settings."""

    graphql: GraphQLConfig
    """GraphQL runtime safeguards and defaults."""


def _load_yaml_config(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    assert isinstance(data, dict), "Configuration file must define a mapping"
    return data


def _env_value(variable_name: str) -> str:
    assert variable_name, "Environment variable name must be non-empty"
    return os.environ[variable_name]


def load_config(config_path: Optional[Path] = None) -> AppConfig:
    path = config_path if config_path is not None else CONFIG_PATH
    raw_config = _load_yaml_config(path)

    neo4j_raw = raw_config["neo4j"]
    graphql_raw = raw_config["graphql"]

    uri = _env_value(neo4j_raw["uri_env"])
    username = _env_value(neo4j_raw["username_env"])
    password = _env_value(neo4j_raw["password_env"])

    database: Optional[str] = None
    if "database_env" in neo4j_raw:
        env_name = neo4j_raw["database_env"]
        if env_name:
            database = _env_value(env_name)

    fetch_timeout_raw = (
        neo4j_raw["fetch_timeout_s"] if "fetch_timeout_s" in neo4j_raw else 5.0
    )
    fetch_timeout = float(fetch_timeout_raw)

    neo4j_config = Neo4jConfig(
        uri=uri,
        username=username,
        password=password,
        database=database,
        fetch_timeout_s=fetch_timeout,
    )

    graphql_config = GraphQLConfig(
        max_depth=graphql_raw["max_depth"],
        default_limit=graphql_raw["default_limit"],
        max_limit=graphql_raw["max_limit"],
    )

    return AppConfig(neo4j=neo4j_config, graphql=graphql_config)
