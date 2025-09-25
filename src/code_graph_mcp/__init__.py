"""Graph MCP aligned with documentation ontology."""

from .ontology import (
    EntityType,
    RelationType,
    ENTITY_TYPES,
    RELATION_TYPES,
    relation_constraints,
    allowed_incoming,
    allowed_outgoing,
    to_graphql_type_name,
    graphql_entity_enum_name,
    entity_type_from_enum,
    graphql_relation_enum_name,
    relation_type_from_enum,
    relation_to_neo4j_label,
)

__all__ = [
    "EntityType",
    "RelationType",
    "ENTITY_TYPES",
    "RELATION_TYPES",
    "relation_constraints",
    "allowed_incoming",
    "allowed_outgoing",
    "to_graphql_type_name",
    "graphql_entity_enum_name",
    "entity_type_from_enum",
    "graphql_relation_enum_name",
    "relation_type_from_enum",
    "relation_to_neo4j_label",
]
