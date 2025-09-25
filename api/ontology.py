from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Set


class EntityType(str, Enum):
    LIBRARY_FRAMEWORK = "Library / Framework"
    MODULE_PACKAGE = "Module / Package"
    CLASS_OBJECT = "Class / Object"
    FUNCTION_METHOD = "Function / Method"
    PARAMETER_OPTION = "Parameter / Option"
    CLI_COMMAND = "CLI Command"
    CONFIG_KEY_FILE = "Config Key / File"
    CONCEPT_TECHNICAL_TERM = "Concept / Technical Term"
    TASK_WORKFLOW = "Task / Workflow"
    CODE_SNIPPET_EXAMPLE = "Code Snippet / Example"
    ERROR_WARNING_GOTCHA = "Error / Warning / Gotcha"
    BEST_PRACTICE_RECOMMENDATION = "Best Practice / Recommendation"
    VERSION_RELEASE = "Version / Release"
    PERFORMANCE_METRIC = "Performance / Metric"
    RATIONALE_DESIGN_REASON = "Rationale / Design Reason"
    EXTERNAL_DEPENDENCY = "External Dependency"
    DOC_SECTION = "Doc Section"


class RelationType(str, Enum):
    IS_PART_OF = "is_part_of"
    HAS_PARAMETER = "has_parameter"
    DEFINED_IN = "defined_in"
    USED_FOR = "used_for"
    CONFIGURED_BY = "configured_by"
    CALLS_DEPENDS_ON = "calls / depends_on"
    PRODUCES = "produces"
    EXPLAINS = "explains"
    EXAMPLE_OF = "example_of"
    ILLUSTRATES = "illustrates"
    WARNS_ABOUT = "warns_about"
    RECOMMENDS = "recommends"
    SIMILAR_TO = "similar_to"
    ALTERNATIVE_TO = "alternative_to"
    DEPRECATED_IN = "deprecated_in"
    SUPERSEDES = "supersedes"
    AFFECTS = "affects"
    IMPROVES = "improves"
    LEADS_TO = "leads_to"
    REQUIRES = "requires"
    JUSTIFIES = "justifies"


ENTITY_TYPES: List[str] = [etype.value for etype in EntityType]
RELATION_TYPES: List[str] = [rtype.value for rtype in RelationType]


@dataclass(frozen=True)
class RelationEndpoints:
    source: Set[str]
    target: Set[str]


_RELATION_ENDPOINTS: Dict[str, RelationEndpoints] = {
    RelationType.IS_PART_OF.value: RelationEndpoints(
        source={
            EntityType.FUNCTION_METHOD.value,
            EntityType.CLASS_OBJECT.value,
            EntityType.MODULE_PACKAGE.value,
        },
        target={
            EntityType.LIBRARY_FRAMEWORK.value,
            EntityType.MODULE_PACKAGE.value,
            EntityType.CLASS_OBJECT.value,
        },
    ),
    RelationType.HAS_PARAMETER.value: RelationEndpoints(
        source={
            EntityType.FUNCTION_METHOD.value,
            EntityType.CLI_COMMAND.value,
        },
        target={EntityType.PARAMETER_OPTION.value},
    ),
    RelationType.DEFINED_IN.value: RelationEndpoints(
        source={
            EntityType.LIBRARY_FRAMEWORK.value,
            EntityType.MODULE_PACKAGE.value,
            EntityType.CLASS_OBJECT.value,
            EntityType.FUNCTION_METHOD.value,
            EntityType.PARAMETER_OPTION.value,
            EntityType.CLI_COMMAND.value,
            EntityType.CONFIG_KEY_FILE.value,
            EntityType.CONCEPT_TECHNICAL_TERM.value,
            EntityType.TASK_WORKFLOW.value,
            EntityType.CODE_SNIPPET_EXAMPLE.value,
            EntityType.ERROR_WARNING_GOTCHA.value,
            EntityType.BEST_PRACTICE_RECOMMENDATION.value,
            EntityType.VERSION_RELEASE.value,
            EntityType.PERFORMANCE_METRIC.value,
            EntityType.RATIONALE_DESIGN_REASON.value,
            EntityType.EXTERNAL_DEPENDENCY.value,
            EntityType.DOC_SECTION.value,
        },
        target={
            EntityType.LIBRARY_FRAMEWORK.value,
            EntityType.VERSION_RELEASE.value,
        },
    ),
    RelationType.USED_FOR.value: RelationEndpoints(
        source={
            EntityType.LIBRARY_FRAMEWORK.value,
            EntityType.MODULE_PACKAGE.value,
            EntityType.CLASS_OBJECT.value,
            EntityType.FUNCTION_METHOD.value,
            EntityType.CLI_COMMAND.value,
            EntityType.CONFIG_KEY_FILE.value,
            EntityType.CONCEPT_TECHNICAL_TERM.value,
            EntityType.TASK_WORKFLOW.value,
            EntityType.BEST_PRACTICE_RECOMMENDATION.value,
            EntityType.EXTERNAL_DEPENDENCY.value,
        },
        target={
            EntityType.TASK_WORKFLOW.value,
            EntityType.CONCEPT_TECHNICAL_TERM.value,
            EntityType.PERFORMANCE_METRIC.value,
        },
    ),
    RelationType.CONFIGURED_BY.value: RelationEndpoints(
        source={
            EntityType.LIBRARY_FRAMEWORK.value,
            EntityType.MODULE_PACKAGE.value,
            EntityType.CLASS_OBJECT.value,
            EntityType.FUNCTION_METHOD.value,
            EntityType.CLI_COMMAND.value,
            EntityType.TASK_WORKFLOW.value,
        },
        target={
            EntityType.CONFIG_KEY_FILE.value,
            EntityType.PARAMETER_OPTION.value,
        },
    ),
    RelationType.CALLS_DEPENDS_ON.value: RelationEndpoints(
        source={
            EntityType.FUNCTION_METHOD.value,
            EntityType.CLASS_OBJECT.value,
            EntityType.MODULE_PACKAGE.value,
            EntityType.CLI_COMMAND.value,
            EntityType.TASK_WORKFLOW.value,
        },
        target={
            EntityType.FUNCTION_METHOD.value,
            EntityType.CLASS_OBJECT.value,
            EntityType.MODULE_PACKAGE.value,
            EntityType.LIBRARY_FRAMEWORK.value,
            EntityType.EXTERNAL_DEPENDENCY.value,
            EntityType.CLI_COMMAND.value,
        },
    ),
    RelationType.PRODUCES.value: RelationEndpoints(
        source={
            EntityType.FUNCTION_METHOD.value,
            EntityType.CLI_COMMAND.value,
            EntityType.TASK_WORKFLOW.value,
        },
        target={
            EntityType.CONCEPT_TECHNICAL_TERM.value,
            EntityType.PERFORMANCE_METRIC.value,
            EntityType.ERROR_WARNING_GOTCHA.value,
        },
    ),
    RelationType.EXPLAINS.value: RelationEndpoints(
        source={
            EntityType.DOC_SECTION.value,
            EntityType.BEST_PRACTICE_RECOMMENDATION.value,
        },
        target={
            EntityType.LIBRARY_FRAMEWORK.value,
            EntityType.MODULE_PACKAGE.value,
            EntityType.CLASS_OBJECT.value,
            EntityType.FUNCTION_METHOD.value,
            EntityType.PARAMETER_OPTION.value,
            EntityType.CLI_COMMAND.value,
            EntityType.CONFIG_KEY_FILE.value,
            EntityType.CONCEPT_TECHNICAL_TERM.value,
            EntityType.TASK_WORKFLOW.value,
            EntityType.EXTERNAL_DEPENDENCY.value,
            EntityType.ERROR_WARNING_GOTCHA.value,
            EntityType.BEST_PRACTICE_RECOMMENDATION.value,
        },
    ),
    RelationType.EXAMPLE_OF.value: RelationEndpoints(
        source={EntityType.CODE_SNIPPET_EXAMPLE.value},
        target={
            EntityType.LIBRARY_FRAMEWORK.value,
            EntityType.MODULE_PACKAGE.value,
            EntityType.CLASS_OBJECT.value,
            EntityType.FUNCTION_METHOD.value,
            EntityType.PARAMETER_OPTION.value,
            EntityType.CLI_COMMAND.value,
            EntityType.CONFIG_KEY_FILE.value,
            EntityType.CONCEPT_TECHNICAL_TERM.value,
            EntityType.TASK_WORKFLOW.value,
            EntityType.BEST_PRACTICE_RECOMMENDATION.value,
            EntityType.EXTERNAL_DEPENDENCY.value,
        },
    ),
    RelationType.ILLUSTRATES.value: RelationEndpoints(
        source={EntityType.CODE_SNIPPET_EXAMPLE.value},
        target={
            EntityType.CONCEPT_TECHNICAL_TERM.value,
            EntityType.TASK_WORKFLOW.value,
            EntityType.PERFORMANCE_METRIC.value,
        },
    ),
    RelationType.WARNS_ABOUT.value: RelationEndpoints(
        source={EntityType.DOC_SECTION.value},
        target={EntityType.ERROR_WARNING_GOTCHA.value},
    ),
    RelationType.RECOMMENDS.value: RelationEndpoints(
        source={EntityType.DOC_SECTION.value},
        target={
            EntityType.BEST_PRACTICE_RECOMMENDATION.value,
            EntityType.TASK_WORKFLOW.value,
            EntityType.FUNCTION_METHOD.value,
            EntityType.CLI_COMMAND.value,
        },
    ),
    RelationType.SIMILAR_TO.value: RelationEndpoints(
        source=set(ENTITY_TYPES) - {EntityType.DOC_SECTION.value},
        target=set(ENTITY_TYPES) - {EntityType.DOC_SECTION.value},
    ),
    RelationType.ALTERNATIVE_TO.value: RelationEndpoints(
        source=set(ENTITY_TYPES) - {EntityType.DOC_SECTION.value},
        target=set(ENTITY_TYPES) - {EntityType.DOC_SECTION.value},
    ),
    RelationType.DEPRECATED_IN.value: RelationEndpoints(
        source=set(ENTITY_TYPES) - {EntityType.VERSION_RELEASE.value},
        target={EntityType.VERSION_RELEASE.value},
    ),
    RelationType.SUPERSEDES.value: RelationEndpoints(
        source=set(ENTITY_TYPES) - {EntityType.DOC_SECTION.value},
        target=set(ENTITY_TYPES) - {EntityType.DOC_SECTION.value},
    ),
    RelationType.AFFECTS.value: RelationEndpoints(
        source={EntityType.PARAMETER_OPTION.value},
        target={EntityType.PERFORMANCE_METRIC.value},
    ),
    RelationType.IMPROVES.value: RelationEndpoints(
        source={
            EntityType.BEST_PRACTICE_RECOMMENDATION.value,
            EntityType.TASK_WORKFLOW.value,
        },
        target={
            EntityType.PERFORMANCE_METRIC.value,
            EntityType.TASK_WORKFLOW.value,
        },
    ),
    RelationType.LEADS_TO.value: RelationEndpoints(
        source={
            EntityType.TASK_WORKFLOW.value,
            EntityType.FUNCTION_METHOD.value,
            EntityType.CLI_COMMAND.value,
        },
        target={
            EntityType.TASK_WORKFLOW.value,
            EntityType.CONCEPT_TECHNICAL_TERM.value,
            EntityType.ERROR_WARNING_GOTCHA.value,
        },
    ),
    RelationType.REQUIRES.value: RelationEndpoints(
        source={
            EntityType.TASK_WORKFLOW.value,
            EntityType.FUNCTION_METHOD.value,
            EntityType.CLASS_OBJECT.value,
            EntityType.MODULE_PACKAGE.value,
            EntityType.CLI_COMMAND.value,
        },
        target={
            EntityType.EXTERNAL_DEPENDENCY.value,
            EntityType.CONFIG_KEY_FILE.value,
            EntityType.CONCEPT_TECHNICAL_TERM.value,
            EntityType.PARAMETER_OPTION.value,
        },
    ),
    RelationType.JUSTIFIES.value: RelationEndpoints(
        source={EntityType.RATIONALE_DESIGN_REASON.value},
        target={
            EntityType.LIBRARY_FRAMEWORK.value,
            EntityType.MODULE_PACKAGE.value,
            EntityType.CLASS_OBJECT.value,
            EntityType.FUNCTION_METHOD.value,
            EntityType.PARAMETER_OPTION.value,
            EntityType.CLI_COMMAND.value,
            EntityType.CONFIG_KEY_FILE.value,
            EntityType.CONCEPT_TECHNICAL_TERM.value,
            EntityType.TASK_WORKFLOW.value,
            EntityType.BEST_PRACTICE_RECOMMENDATION.value,
            EntityType.EXTERNAL_DEPENDENCY.value,
        },
    ),
}


def relation_constraints(relation_type: str) -> RelationEndpoints:
    try:
        return _RELATION_ENDPOINTS[relation_type]
    except KeyError as exc:  # pragma: no cover
        raise AssertionError(f"Unknown relation type '{relation_type}'") from exc


def allowed_outgoing(entity_type: str) -> Set[str]:
    allowed: Set[str] = set()
    for rel, endpoints in _RELATION_ENDPOINTS.items():
        if entity_type in endpoints.source:
            allowed.add(rel)
    return allowed


def allowed_incoming(entity_type: str) -> Set[str]:
    allowed: Set[str] = set()
    for rel, endpoints in _RELATION_ENDPOINTS.items():
        if entity_type in endpoints.target:
            allowed.add(rel)
    return allowed


def to_graphql_type_name(entity_type: str) -> str:
    parts = [
        part
        for part in entity_type.replace("-", " ").replace("/", " ").split(" ")
        if part
    ]
    words = [part.capitalize() for part in parts]
    sanitized = "".join(words)
    assert sanitized, f"Cannot derive GraphQL type name for '{entity_type}'"
    return sanitized


def graphql_entity_enum_name(entity_type: str) -> str:
    assert entity_type in ENTITY_TYPES, f"Unknown entity type '{entity_type}'"
    return entity_type.upper().replace(" / ", "_").replace(" ", "_")


def entity_type_from_enum(enum_value: str) -> str:
    conversions = {
        graphql_entity_enum_name(entity_type): entity_type
        for entity_type in ENTITY_TYPES
    }
    try:
        return conversions[enum_value]
    except KeyError as exc:  # pragma: no cover
        raise AssertionError(f"Unknown entity enum '{enum_value}'") from exc


def graphql_relation_enum_name(relation_type: str) -> str:
    assert relation_type in RELATION_TYPES, f"Unknown relation type '{relation_type}'"
    return relation_type.upper().replace(" / ", "_")


def relation_type_from_enum(enum_value: str) -> str:
    conversions = {
        graphql_relation_enum_name(relation_type): relation_type
        for relation_type in RELATION_TYPES
    }
    try:
        return conversions[enum_value]
    except KeyError as exc:  # pragma: no cover
        raise AssertionError(f"Unknown relation enum '{enum_value}'") from exc


def relation_to_neo4j_label(relation_type: str) -> str:
    assert relation_type in RELATION_TYPES, f"Unknown relation type '{relation_type}'"
    label = relation_type.upper()
    label = label.replace(" ", "_").replace("/", "_")
    label = "".join(char if char.isalnum() or char == "_" else "_" for char in label)
    return label
