"""Deterministic runtime assurance between an agent and robot actuators."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Mapping


class Outcome(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"


@dataclass(frozen=True)
class Action:
    name: str
    parameters: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Rule:
    name: str
    applies_to: frozenset[str]
    check: Callable[[Action, Mapping[str, Any]], bool]
    outcome: Outcome = Outcome.DENY
    required_context: frozenset[str] = frozenset()


@dataclass(frozen=True)
class Decision:
    action: Action
    outcome: Outcome
    reasons: tuple[str, ...]
    sequence: int


class Guardian:
    """Fail-closed policy gateway with a replayable in-memory audit trail."""

    def __init__(self, rules: list[Rule] | None = None) -> None:
        self.rules = rules or default_rules()
        self.audit_log: list[Decision] = []

    def evaluate(self, action: Action, context: Mapping[str, Any]) -> Decision:
        violations: list[tuple[str, Outcome]] = []
        for rule in self.rules:
            if action.name not in rule.applies_to and "*" not in rule.applies_to:
                continue
            missing = rule.required_context.difference(context)
            if missing:
                violations.append((f"missing_context:{','.join(sorted(missing))}", Outcome.DENY))
                continue
            try:
                passed = bool(rule.check(action, context))
            except Exception:  # a broken rule or malformed input must not allow motion
                violations.append((f"rule_error:{rule.name}", Outcome.DENY))
                continue
            if not passed:
                violations.append((rule.name, rule.outcome))

        if any(outcome is Outcome.DENY for _, outcome in violations):
            outcome = Outcome.DENY
        elif violations:
            outcome = Outcome.REQUIRE_APPROVAL
        else:
            outcome = Outcome.ALLOW

        decision = Decision(
            action=action,
            outcome=outcome,
            reasons=tuple(reason for reason, _ in violations),
            sequence=len(self.audit_log) + 1,
        )
        self.audit_log.append(decision)
        return decision


def default_rules() -> list[Rule]:
    return [
        Rule(
            name="emergency_stop",
            applies_to=frozenset({"*"}),
            required_context=frozenset({"estop"}),
            check=lambda _action, ctx: not bool(ctx["estop"]),
        ),
        Rule(
            name="human_proximity",
            applies_to=frozenset({"move_base", "move_arm"}),
            required_context=frozenset({"human_distance_m"}),
            check=lambda action, ctx: float(ctx["human_distance_m"])
            >= (1.2 if float(action.parameters.get("speed_mps", 0.0)) > 0.5 else 0.5),
        ),
        Rule(
            name="speed_limit",
            applies_to=frozenset({"move_base"}),
            check=lambda action, _ctx: float(action.parameters.get("speed_mps", 0.0)) <= 1.0,
        ),
        Rule(
            name="high_force_requires_approval",
            applies_to=frozenset({"grasp", "move_arm"}),
            check=lambda action, _ctx: float(action.parameters.get("force_n", 0.0)) <= 25.0,
            outcome=Outcome.REQUIRE_APPROVAL,
        ),
    ]
