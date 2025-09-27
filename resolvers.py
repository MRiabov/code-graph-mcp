from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from ariadne import (
    InterfaceType,
    ObjectType,
    QueryType,
    UnionType,
    make_executable_schema,
)

from api.config import AppConfig
from api.errors import QueryLimitError, ValidationError
from api.repository import GraphRepository
from api.schema_builder import GraphQLSchemaSpec, GraphQLEntitySpec, build_schema_sdl
from api.ontology import (
    entity_type_from_enum,
    relation_type_from_enum,
    to_graphql_type_name,
)


@dataclass(frozen=True)
class ResolversBundle:
    schema_spec: GraphQLSchemaSpec
    executable_schema: Any


def _resolve_entity_type(obj: Dict[str, Any], *_: Any) -> str:
    entity_type = obj["type"]
    assert entity_type, "Entity payload requires 'type'"
    return to_graphql_type_name(entity_type)


def _resolve_union_type(obj: Dict[str, Any], *_: Any) -> str:
    return _resolve_entity_type(obj)


def _build_object_type(
    spec: GraphQLEntitySpec,
    config: AppConfig,
) -> ObjectType:
    object_type = ObjectType(spec.graphql_type)

    for field in spec.relation_fields:

        def relation_resolver(
            obj: Dict[str, Any],
            info,
            limit: int = config.graphql.default_limit,
            offset: int = 0,
            relation_type: str = field.relation_type,
        ) -> List[Dict[str, Any]]:
            repo: GraphRepository = info.context["repo"]
            effective_limit = (
                limit if limit is not None else config.graphql.default_limit
            )
            if effective_limit > config.graphql.max_limit:
                raise QueryLimitError(
                    f"Requested limit {effective_limit} exceeds max {config.graphql.max_limit}",
                    max_limit=config.graphql.max_limit,
                    requested=effective_limit,
                )
            if effective_limit < 0:
                raise ValidationError("Limit must be non-negative")
            if offset < 0:
                raise ValidationError("Offset must be non-negative")
            return repo.fetch_relation_targets(
                source_id=obj["id"],
                relation_type=relation_type,
                direction="OUTGOING",
                limit=effective_limit,
                offset=offset,
            )

        object_type.set_field(field.field_name, relation_resolver)

    return object_type


def build_resolvers_bundle(config: AppConfig) -> ResolversBundle:
    schema_spec = build_schema_sdl()

    type_defs = schema_spec.sdl

    query = QueryType()

    @query.field("entity")
    def resolve_entity(*_, id: str):
        repo: GraphRepository = _[1].context["repo"]
        return repo.fetch_entity(id)

    @query.field("entities")
    def resolve_entities(
        *_, type: str = None, search: str = None, limit: int = None, offset: int = 0
    ):
        repo: GraphRepository = _[1].context["repo"]
        graphql_config = repo.graphql_config
        effective_limit = limit if limit is not None else graphql_config.default_limit
        if type is not None:
            try:
                type = entity_type_from_enum(type)
            except AssertionError as exc:  # pragma: no cover
                raise ValidationError(str(exc)) from exc
        if effective_limit > graphql_config.max_limit:
            raise QueryLimitError(
                f"Requested limit {effective_limit} exceeds max {graphql_config.max_limit}",
                max_limit=graphql_config.max_limit,
                requested=effective_limit,
            )
        if effective_limit < 0:
            raise ValidationError("Limit must be non-negative")
        if offset < 0:
            raise ValidationError("Offset must be non-negative")
        return repo.fetch_entities(type, search, effective_limit, offset)

    @query.field("relations")
    def resolve_relations(
        *_,
        sourceId: str,
        relation: str,
        direction: str = "OUTGOING",
        limit: int = None,
        offset: int = 0,
    ):
        repo: GraphRepository = _[1].context["repo"]
        graphql_config = repo.graphql_config
        effective_limit = limit if limit is not None else graphql_config.default_limit
        if effective_limit > graphql_config.max_limit:
            raise QueryLimitError(
                f"Requested limit {effective_limit} exceeds max {graphql_config.max_limit}",
                max_limit=graphql_config.max_limit,
                requested=effective_limit,
            )
        if effective_limit < 0:
            raise ValidationError("Limit must be non-negative")
        if offset < 0:
            raise ValidationError("Offset must be non-negative")
        try:
            relation_type = relation_type_from_enum(relation)
        except AssertionError as exc:  # pragma: no cover
            raise ValidationError(str(exc)) from exc
        direction_value = direction.upper() if direction else "OUTGOING"
        if direction_value not in {"OUTGOING", "INCOMING"}:
            raise ValidationError(
                f"Unsupported relation direction '{direction}'. Use OUTGOING or INCOMING.",
                hint="Use RelationDirection enum values.",
            )
        return repo.fetch_relation_targets(
            source_id=sourceId,
            relation_type=relation_type,
            direction=direction_value,
            limit=effective_limit,
            offset=offset,
        )

    entity_interface = InterfaceType("Entity")
    entity_interface.set_type_resolver(_resolve_entity_type)

    object_types: List[ObjectType] = []
    for entity_spec in schema_spec.entity_specs:
        object_types.append(_build_object_type(entity_spec, config))

    union_types: List[UnionType] = []
    for union_name, members in schema_spec.unions.items():
        union = UnionType(union_name, type_resolver=_resolve_union_type)
        union_types.append(union)

    executable_schema = make_executable_schema(
        type_defs,
        query,
        entity_interface,
        *object_types,
        *union_types,
    )

    return ResolversBundle(schema_spec=schema_spec, executable_schema=executable_schema)
