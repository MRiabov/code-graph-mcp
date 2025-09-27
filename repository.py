from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from neo4j.graph import Node

from api.config import GraphQLConfig
from api.neo4j_client import Neo4jClient
from api.ontology import relation_to_neo4j_label


@dataclass
class GraphRepository:
    neo4j: Neo4jClient
    graphql_config: GraphQLConfig

    def fetch_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        query = """
        MATCH (n {id: $id})
        RETURN n AS node
        LIMIT 1
        """
        records = self.neo4j.run_query_with_timeout(
            query,
            {"id": entity_id},
            timeout_s=self.neo4j.config.fetch_timeout_s,
        )
        if not records:
            return None
        row = records[0]
        node = row["node"]
        return self._serialize_node(node)

    def fetch_entities(
        self,
        entity_type: Optional[str],
        search: Optional[str],
        limit: int,
        offset: int,
    ) -> List[Dict[str, Any]]:
        assert limit <= self.graphql_config.max_limit, (
            "Limit exceeds configured maximum"
        )
        assert limit >= 0, "Limit must be non-negative"
        assert offset >= 0, "Offset must be non-negative"
        query_parts = ["MATCH (n)"]
        where_clauses = []
        parameters: Dict[str, Any] = {"limit": limit, "offset": offset}
        if entity_type:
            where_clauses.append("n.type = $type")
            parameters["type"] = entity_type
        if search:
            where_clauses.append("toLower(n.name) CONTAINS toLower($search)")
            parameters["search"] = search
        if where_clauses:
            query_parts.append("WHERE " + " AND ".join(where_clauses))
        query_parts.append("RETURN n AS node")
        query_parts.append("SKIP $offset")
        query_parts.append("LIMIT $limit")
        query = "\n".join(query_parts)
        records = self.neo4j.run_query_with_timeout(query, parameters)
        nodes: List[Dict[str, Any]] = []
        for row in records:
            node = row["node"]
            nodes.append(self._serialize_node(node))
        return nodes

    def fetch_relation_targets(
        self,
        *,
        source_id: str,
        relation_type: str,
        direction: str,
        limit: int,
        offset: int,
    ) -> List[Dict[str, Any]]:
        assert limit <= self.graphql_config.max_limit, (
            "Limit exceeds configured maximum"
        )
        assert limit >= 0, "Limit must be non-negative"
        assert offset >= 0, "Offset must be non-negative"
        label = relation_to_neo4j_label(relation_type)
        if direction == "OUTGOING":
            pattern = f"(src)-[:{label}]->(dst)"
        else:
            assert direction == "INCOMING", "Unsupported relation direction"
            pattern = f"(dst)-[:{label}]->(src)"
        query = (
            "MATCH (src {id: $source_id})\n"
            f"MATCH {pattern}\n"
            "RETURN DISTINCT dst AS node\n"
            "SKIP $offset\n"
            "LIMIT $limit"
        )
        records = self.neo4j.run_query_with_timeout(
            query,
            {
                "source_id": source_id,
                "offset": offset,
                "limit": limit,
            },
        )
        nodes: List[Dict[str, Any]] = []
        for row in records:
            node = row["node"]
            nodes.append(self._serialize_node(node))
        return nodes

    @staticmethod
    def _serialize_node(node: Any) -> Dict[str, Any]:
        if isinstance(node, Node):
            payload = dict(node)
            payload.setdefault("labels", sorted(node.labels))
            return payload
        assert isinstance(node, dict), "Unexpected node payload type"
        return node
