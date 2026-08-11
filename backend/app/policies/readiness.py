from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence


@dataclass(frozen=True)
class ReadinessVerdict:
    overall_status: str
    can_proceed: bool
    reason: str
    missing_domains: tuple[str, ...] = field(default_factory=tuple)
    unavailable_domains: tuple[str, ...] = field(default_factory=tuple)
    blocked_domains: tuple[str, ...] = field(default_factory=tuple)
    warning_domains: tuple[str, ...] = field(default_factory=tuple)


def calculate_readiness(domain_statuses: dict[str, str | None], required_domains: Sequence[str]) -> ReadinessVerdict:
    missing = tuple(d for d in required_domains if domain_statuses.get(d) is None)
    if missing:
        return ReadinessVerdict("NOT_READY", False, f"Assessment required for: {', '.join(missing)}.", missing_domains=missing)
    unavailable = tuple(d for d in required_domains if domain_statuses.get(d) == "UNAVAILABLE")
    if unavailable:
        return ReadinessVerdict("NOT_READY", False, f"Assessment unavailable for: {', '.join(unavailable)}. Re-run required.", unavailable_domains=unavailable)
    blocked = tuple(d for d in required_domains if domain_statuses.get(d) == "BLOCKED")
    if blocked:
        return ReadinessVerdict("BLOCKED", False, f"Blocking issue(s) in: {', '.join(blocked)}.", blocked_domains=blocked)
    warning = tuple(d for d in required_domains if domain_statuses.get(d) == "WARNING")
    if warning:
        return ReadinessVerdict("WARNING", False, f"Warning(s) in: {', '.join(warning)}. Review recommended before proceeding.", warning_domains=warning)
    return ReadinessVerdict("READY", True, "All required domains are ready.")
