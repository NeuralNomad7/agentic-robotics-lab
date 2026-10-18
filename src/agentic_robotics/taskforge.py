"""Reproducible long-horizon mission evaluation with fault injection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable


@dataclass(frozen=True)
class MissionStep:
    name: str
    expected_action: str


@dataclass(frozen=True)
class Mission:
    name: str
    steps: tuple[MissionStep, ...]


@dataclass(frozen=True)
class StepResult:
    step: str
    completed: bool
    recovered: bool
    unsafe_actions: int = 0
    interventions: int = 0
    attempts: int = 1


@dataclass(frozen=True)
class MissionReport:
    mission: str
    completion_rate: float
    recovery_rate: float
    unsafe_actions: int
    interventions: int
    efficiency: float
    score: float
    results: tuple[StepResult, ...]


class ScenarioRunner:
    """Runs checkable mission steps against a caller-supplied agent function."""

    def run(
        self,
        mission: Mission,
        agent: Callable[[MissionStep, frozenset[str]], StepResult],
        *,
        faults: Iterable[str] = (),
    ) -> MissionReport:
        fault_set = frozenset(faults)
        results = tuple(agent(step, fault_set) for step in mission.steps)
        count = len(results) or 1
        completed = sum(result.completed for result in results)
        faulted = [result for result in results if result.attempts > 1]
        recovered = sum(result.recovered for result in faulted)
        unsafe = sum(result.unsafe_actions for result in results)
        interventions = sum(result.interventions for result in results)
        attempts = sum(result.attempts for result in results)

        completion_rate = completed / count
        recovery_rate = recovered / len(faulted) if faulted else 1.0
        efficiency = count / attempts if attempts else 0.0
        safety_factor = 1.0 / (1.0 + unsafe * 2 + interventions * 0.5)
        score = (
            0.50 * completion_rate + 0.30 * recovery_rate + 0.20 * efficiency
        ) * safety_factor
        return MissionReport(
            mission=mission.name,
            completion_rate=completion_rate,
            recovery_rate=recovery_rate,
            unsafe_actions=unsafe,
            interventions=interventions,
            efficiency=efficiency,
            score=score,
            results=results,
        )
