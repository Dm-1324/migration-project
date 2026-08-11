from __future__ import annotations

from dataclasses import dataclass

from app.models.migration import LIFECYCLE_STATES

V1_REACHABLE_STATES = ("RECEIVED", "DISCOVERED", "ASSESSED", "PREPARED", "PREFLIGHT_PASS", "READY")
READINESS_GATED_STATES = {"PREFLIGHT_PASS", "READY"}


@dataclass(frozen=True)
class TransitionDecision:
    allowed: bool
    reason: str


def can_transition(current_state: str, target_state: str, overall_readiness_status: str | None) -> TransitionDecision:
    if target_state not in LIFECYCLE_STATES:
        return TransitionDecision(False, f"'{target_state}' is not a recognized lifecycle state.")
    if target_state not in V1_REACHABLE_STATES:
        return TransitionDecision(False, f"'{target_state}' is reserved for a later phase and cannot be entered in V1.")
    if current_state not in V1_REACHABLE_STATES:
        return TransitionDecision(False, f"Current state '{current_state}' is not valid for a V1 transition.")
    current_idx = V1_REACHABLE_STATES.index(current_state)
    target_idx = V1_REACHABLE_STATES.index(target_state)
    if target_idx <= current_idx:
        return TransitionDecision(False, f"Cannot move from '{current_state}' to '{target_state}' -- lifecycle only moves forward.")
    if target_state in READINESS_GATED_STATES and overall_readiness_status != "READY":
        return TransitionDecision(False, f"Cannot enter '{target_state}': current overall readiness is '{overall_readiness_status or 'NOT_ASSESSED'}', not READY.")
    return TransitionDecision(True, f"'{current_state}' -> '{target_state}' is permitted.")
