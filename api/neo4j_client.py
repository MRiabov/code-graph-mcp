from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError

from api.errors import InternalServerError

from api.config import Neo4jConfig


@dataclass
class Neo4jClient:
    config: Neo4jConfig

    def __post_init__(self) -> None:
        self._driver = GraphDatabase.driver(
            self.config.uri,
            auth=(self.config.username, self.config.password),
        )

    def close(self) -> None:
        self._driver.close()

    def run_query(
        self, cypher: str, parameters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        try:
            with self._driver.session(database=self.config.database) as session:
                result = session.run(cypher, parameters or {})
                return [record.data() for record in result]
        except Neo4jError as exc:  # pragma: no cover
            raise InternalServerError("Neo4j query failed", hint=str(exc)) from exc

    def run_query_with_timeout(
        self,
        cypher: str,
        parameters: Optional[Dict[str, Any]] = None,
        timeout_s: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        tx_metadata = {}
        tx_timeout = timeout_s or self.config.fetch_timeout_s
        try:
            with self._driver.session(database=self.config.database) as session:
                result = session.run(
                    cypher,
                    parameters or {},
                    timeout=tx_timeout,
                    metadata=tx_metadata,
                )
                return [record.data() for record in result]
        except Neo4jError as exc:  # pragma: no cover
            raise InternalServerError("Neo4j query failed", hint=str(exc)) from exc

    def run_read_transaction(
        self,
        work,
        timeout_s: Optional[float] = None,
    ) -> Iterable[Dict[str, Any]]:
        tx_timeout = timeout_s or self.config.fetch_timeout_s
        with self._driver.session(database=self.config.database) as session:
            return session.execute_read(work, timeout=tx_timeout)
