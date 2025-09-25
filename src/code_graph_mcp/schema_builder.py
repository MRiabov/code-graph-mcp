from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Set, Tuple
import re

from .ontology import (
    ENTITY_TYPES,
    RELATION_TYPES,
    allowed_outgoing,
    relation_constraints,
    to_graphql_type_name,
)


@dataclass(frozen=True)
class GraphQLRelationField:
    field_name: str
    relation_type: str
    target_types: Tuple[str, ...]
    target_union: Optional[str]


@dataclass(frozen=True)
class GraphQLEntitySpec:
    graphql_type: str
    entity_type: str
    relation_fields: Tuple[GraphQLRelationField, ...]


@dataclass(frozen=True)
class GraphQLSchemaSpec:
    sdl: str
    entity_specs: Tuple[GraphQLEntitySpec, ...]
    unions: Dict[str, Tuple[str, ...]]


def _to_pascal_case(value: str) -> str:
    tokens = re.split(r"[^a-zA-Z0-9]+", value)
    parts = [token.capitalize() for token in tokens if token]
    result = "".join(parts)
    assert result, f"Cannot convert '{value}' to PascalCase"
    return result


def _to_camel_case(value: str) -> str:
    pascal = _to_pascal_case(value)
    return pascal[0].lower() + pascal[1:]


def _create_relation_field(
    relation_type: str, target_entity_types: Sequence[str]
) -> GraphQLRelationField:
    field_name = _to_camel_case(relation_type)
    target_graphql_types = tuple(
        to_graphql_type_name(target_type)
        for target_type in sorted(set(target_entity_types))
    )
    if len(target_graphql_types) == 1:
        union_name: Optional[str] = None
    else:
        union_name = f"{_to_pascal_case(relation_type)}Targets"
    return GraphQLRelationField(
        field_name=field_name,
        relation_type=relation_type,
        target_types=target_graphql_types,
        target_union=union_name,
    )


def _build_entity_specs() -> Tuple[GraphQLEntitySpec, ...]:
    specs: List[GraphQLEntitySpec] = []
    for entity_type in ENTITY_TYPES:
        relation_fields: List[GraphQLRelationField] = []
        outgoing = allowed_outgoing(entity_type)
        for relation_type in sorted(outgoing):
            endpoints = relation_constraints(relation_type)
            field = _create_relation_field(
                relation_type=relation_type,
                target_entity_types=sorted(endpoints.target),
            )
            relation_fields.append(field)
        specs.append(
            GraphQLEntitySpec(
                graphql_type=to_graphql_type_name(entity_type),
                entity_type=entity_type,
                relation_fields=tuple(relation_fields),
            )
        )
    return tuple(specs)


def build_schema_sdl() -> GraphQLSchemaSpec:
    entity_specs = _build_entity_specs()
    lines: List[str] = []

    # Enums
    lines.append("enum EntityType {")
    for entity_type in ENTITY_TYPES:
        enum_name = entity_type.upper().replace(" / ", "_").replace(" ", "_")
        lines.append(f"  {enum_name}")
    lines.append("}\n")

    lines.append("enum RelationType {")
    for relation_type in RELATION_TYPES:
        enum_name = relation_type.upper().replace(" / ", "_")
        lines.append(f"  {enum_name}")
    lines.append("}\n")

    lines.append("enum RelationDirection {")
    lines.append("  OUTGOING")
    lines.append("  INCOMING")
    lines.append("}\n")

    # Interface shared fields
    lines.append("interface Entity {")
    lines.append("  id: ID!")
    lines.append("  type: EntityType!")
    lines.append("  name: String!")
    lines.append("  description: String")
    lines.append("  snippet: String")
    lines.append("  source: String")
    lines.append("  version: String")
    lines.append("  tags: [String!]")
    lines.append("  embedding: [Float!]")
    lines.append("  confidence: Float")
    lines.append("}\n")

    # Collect union definitions for relation targets
    unions: Dict[str, Set[str]] = {}

    # Entity types
    for spec in entity_specs:
        lines.append(f"type {spec.graphql_type} implements Entity {{")
        lines.append("  id: ID!")
        lines.append("  type: EntityType!")
        lines.append("  name: String!")
        lines.append("  description: String")
        lines.append("  snippet: String")
        lines.append("  source: String")
        lines.append("  version: String")
        lines.append("  tags: [String!]")
        lines.append("  embedding: [Float!]")
        lines.append("  confidence: Float")
        for field in spec.relation_fields:
            if field.target_union:
                unions.setdefault(field.target_union, set()).update(field.target_types)
                target = field.target_union
            else:
                target = field.target_types[0]
            lines.append(
                f"  {field.field_name}(limit: Int = 25, offset: Int = 0): [{target}!]!"
            )
        lines.append("}\n")

    for union_name, members in sorted(unions.items()):
        members_list = " | ".join(sorted(members))
        lines.append(f"union {union_name} = {members_list}\n")

    # Root query
    lines.append("type Query {")
    lines.append("  entity(id: ID!): Entity")
    lines.append(
        "  entities(type: EntityType, search: String, limit: Int = 25, offset: Int = 0): [Entity!]!"
    )
    lines.append(
        "  relations(sourceId: ID!, relation: RelationType!, direction: RelationDirection = OUTGOING, limit: Int = 25, offset: Int = 0): [Entity!]!"
    )
    lines.append("}\n")

    sdl = "\n".join(lines)
    unions_final = {name: tuple(sorted(members)) for name, members in unions.items()}
    return GraphQLSchemaSpec(
        sdl=sdl,
        entity_specs=entity_specs,
        unions=unions_final,
    )
