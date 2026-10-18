"""Temporal, provenance-aware memory for changing physical environments."""

from __future__ import annotations

import math
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class Observation:
    entity: str
    value: str
    confidence: float
    source: str
    location: str | None
    observed_at: float


@dataclass(frozen=True)
class Belief:
    entity: str
    value: str
    confidence: float
    source: str
    location: str | None
    age_seconds: float
    supporting_observations: int


class WorldMemory:
    """Append-only observations with decayed, contradiction-aware recall."""

    def __init__(
        self, half_life_seconds: float = 300.0, contradiction_discount: float = 0.5
    ) -> None:
        if half_life_seconds <= 0:
            raise ValueError("half_life_seconds must be positive")
        if not 0.0 <= contradiction_discount <= 1.0:
            raise ValueError("contradiction_discount must be between 0 and 1")
        self.half_life_seconds = half_life_seconds
        # Weight kept by an observation once a newer one reports a different value.
        # The older observation stays in the log; it just counts for less.
        self.contradiction_discount = contradiction_discount
        self.observations: list[Observation] = []

    def observe(
        self,
        entity: str,
        value: str,
        *,
        confidence: float,
        source: str,
        location: str | None = None,
        observed_at: float | None = None,
    ) -> Observation:
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        observation = Observation(
            entity=entity,
            value=value,
            confidence=confidence,
            source=source,
            location=location,
            observed_at=time.time() if observed_at is None else observed_at,
        )
        self.observations.append(observation)
        return observation

    def recall(
        self, entity: str, *, location: str | None = None, now: float | None = None
    ) -> Belief | None:
        current_time = time.time() if now is None else now
        candidates = [
            item
            for item in self.observations
            if item.entity == entity and (location is None or item.location == location)
        ]
        if not candidates:
            return None

        scores: dict[str, float] = {}
        newest: dict[str, Observation] = {}
        counts: dict[str, int] = {}
        for item in candidates:
            age = max(0.0, current_time - item.observed_at)
            decayed = item.confidence * math.pow(0.5, age / self.half_life_seconds)
            contradicted = any(
                other.value != item.value and other.observed_at > item.observed_at
                for other in candidates
            )
            if contradicted:
                decayed *= self.contradiction_discount
            scores[item.value] = scores.get(item.value, 0.0) + decayed
            counts[item.value] = counts.get(item.value, 0) + 1
            if item.value not in newest or item.observed_at > newest[item.value].observed_at:
                newest[item.value] = item

        winning_value = max(scores, key=lambda value: (scores[value], newest[value].observed_at))
        winner = newest[winning_value]
        total = sum(scores.values())
        normalized_confidence = scores[winning_value] / total if total else 0.0
        return Belief(
            entity=entity,
            value=winning_value,
            confidence=normalized_confidence,
            source=winner.source,
            location=winner.location,
            age_seconds=max(0.0, current_time - winner.observed_at),
            supporting_observations=counts[winning_value],
        )
