import unittest

from agentic_robotics.taskforge import Mission, MissionStep, ScenarioRunner, StepResult


class TaskForgeTests(unittest.TestCase):
    def test_unsafe_success_is_penalized(self) -> None:
        mission = Mission("pick", (MissionStep("grasp", "grasp"),))
        safe = ScenarioRunner().run(
            mission, lambda step, faults: StepResult(step.name, True, False)
        )
        unsafe = ScenarioRunner().run(
            mission,
            lambda step, faults: StepResult(step.name, True, False, unsafe_actions=1),
        )
        self.assertLess(unsafe.score, safe.score)

    def test_recovery_is_measured(self) -> None:
        mission = Mission("move", (MissionStep("navigate", "move_base"),))
        report = ScenarioRunner().run(
            mission,
            lambda step, faults: StepResult(step.name, True, True, attempts=2),
            faults={"navigate"},
        )
        self.assertEqual(report.recovery_rate, 1.0)
        self.assertLess(report.efficiency, 1.0)

    def test_incomplete_mission_scores_lower(self) -> None:
        mission = Mission("two", (MissionStep("a", "x"), MissionStep("b", "y")))
        full = ScenarioRunner().run(mission, lambda s, f: StepResult(s.name, True, False))
        half = ScenarioRunner().run(
            mission, lambda s, f: StepResult(s.name, s.name == "a", False)
        )
        self.assertEqual(half.completion_rate, 0.5)
        self.assertLess(half.score, full.score)


if __name__ == "__main__":
    unittest.main()
