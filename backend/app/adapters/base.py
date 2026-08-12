from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResourceCheckResult:
    status: str
    code: str | None
    severity: str | None
    message: str
    tool: str
    raw_output: str
