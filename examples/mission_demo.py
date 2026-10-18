"""End-to-end demonstration of the four reference systems."""

from __future__ import annotations

from agentic_robotics import (
    Action,
    FleetCoordinator,
    Guardian,
    Mission,
    MissionStep,
    Outcome,
    Robot,
    ScenarioRunner,
    Task,
    WorldMemory,
)
from agentic_robotics.taskforge import StepResult


def main() -> None:
    now = 1_000.0
    fleet = FleetCoordinator()
    fleet.register(Robot("mobile-01", frozenset({"transport"}), (0, 0), 0.82, last_heartbeat=now))
    fleet.register(Robot("mobile-02", frozenset({"transport"}), (8, 2), 0.95, last_heartbeat=now))
    lease = fleet.allocate(Task("deliver-kit", "transport", (2, 1)), now)

    memory = WorldMemory(half_life_seconds=120)
    memory.observe("kit", "station-a", confidence=0.94, source="overhead-camera", observed_at=now)
    guardian = Guardian()
    decision = guardian.evaluate(
        Action("move_base", {"speed_mps": 0.4}),
        {"estop": False, "human_distance_m": 1.5},
    )

    mission = Mission(
        "warehouse-kit-delivery",
        (
            MissionStep("locate-kit", "observe"),
            MissionStep("navigate-to-kit", "move_base"),
            MissionStep("deliver-kit", "move_base"),
        ),
    )

    def demo_agent(step: MissionStep, faults: frozenset[str]) -> StepResult:
        disturbed = step.name in faults
        return StepResult(
            step=step.name,
            completed=True,
            recovered=disturbed,
            attempts=2 if disturbed else 1,
        )

    report = ScenarioRunner().run(mission, demo_agent, faults={"navigate-to-kit"})
    print(f"assigned robot : {lease.robot_id if lease else 'none'}")
    print(f"safety decision: {decision.outcome.value}")
    print(f"remembered kit : {memory.recall('kit', now=now).value}")
    print(f"mission score  : {report.score:.3f}")
    assert decision.outcome is Outcome.ALLOW


if __name__ == "__main__":
    main()
