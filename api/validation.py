from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Set

from graphql import GraphQLError
from graphql.language import FragmentDefinitionNode, SelectionSetNode
from graphql.validation import ValidationContext, ValidationRule


@dataclass(frozen=True)
class DepthLimitConfig:
    max_depth: int


class DepthLimitRule(ValidationRule):
    def __init__(self, context: ValidationContext, config: DepthLimitConfig) -> None:
        super().__init__(context)
        self._config = config

    def enter_operation_definition(self, node, *_):  # type: ignore[override]
        if not node.selection_set:
            return node
        depth = self._measure_depth(node.selection_set, 0, set())
        if depth > self._config.max_depth:
            message = f"Query depth {depth} exceeds the configured maximum depth {self._config.max_depth}"
            self.report_error(GraphQLError(message, [node]))
        return node

    def _measure_depth(
        self,
        selection_set: SelectionSetNode,
        base_depth: int,
        visited_fragments: Set[str],
    ) -> int:
        max_depth = base_depth
        for selection in selection_set.selections:
            kind = selection.kind
            if kind == "field":
                name = selection.name.value
                if name.startswith("__"):
                    continue
                next_depth = base_depth + 1
                if selection.selection_set:
                    next_depth = self._measure_depth(
                        selection.selection_set,
                        base_depth + 1,
                        visited_fragments,
                    )
                if next_depth > max_depth:
                    max_depth = next_depth
            elif kind == "inline_fragment" and selection.selection_set:
                inline_depth = self._measure_depth(
                    selection.selection_set,
                    base_depth,
                    visited_fragments,
                )
                if inline_depth > max_depth:
                    max_depth = inline_depth
            elif kind == "fragment_spread":
                name = selection.name.value
                if name in visited_fragments:
                    continue
                visited_fragments.add(name)
                fragment = self._get_fragment(name)
                if fragment and fragment.selection_set:
                    fragment_depth = self._measure_depth(
                        fragment.selection_set,
                        base_depth,
                        visited_fragments,
                    )
                    if fragment_depth > max_depth:
                        max_depth = fragment_depth
                visited_fragments.remove(name)
        return max_depth

    def _get_fragment(self, name: str) -> Optional[FragmentDefinitionNode]:
        return self.context.get_fragment(name)


def depth_limit_rule_factory(max_depth: int):
    config = DepthLimitConfig(max_depth=max_depth)

    def _factory(context: ValidationContext) -> DepthLimitRule:
        return DepthLimitRule(context, config)

    return _factory
