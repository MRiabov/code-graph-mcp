from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class StructuredError(Exception):
    error_type: str
    message: str
    hint: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "type": self.error_type,
            "message": self.message,
        }
        if self.hint:
            payload["hint"] = self.hint
        if self.details:
            payload["details"] = self.details
        return payload


class ValidationError(StructuredError):
    def __init__(
        self,
        message: str,
        *,
        hint: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__("ValidationError", message, hint, details or {})


class QueryLimitError(StructuredError):
    def __init__(self, message: str, *, max_limit: int, requested: int):
        details = {"max_limit": max_limit, "requested": requested}
        super().__init__("QueryLimitError", message, None, details)


class NotFoundError(StructuredError):
    def __init__(self, message: str):
        super().__init__("NotFoundError", message)


class InternalServerError(StructuredError):
    def __init__(self, message: str, *, hint: Optional[str] = None):
        super().__init__("InternalServerError", message, hint)
