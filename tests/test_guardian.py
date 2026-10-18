import unittest

from agentic_robotics.guardian import Action, Guardian, Outcome


class GuardianTests(unittest.TestCase):
    def setUp(self) -> None:
        self.guardian = Guardian()

    def test_denies_motion_near_a_human(self) -> None:
        decision = self.guardian.evaluate(
            Action("move_base", {"speed_mps": 0.7}),
            {"estop": False, "human_distance_m": 0.8},
        )
        self.assertEqual(decision.outcome, Outcome.DENY)
        self.assertIn("human_proximity", decision.reasons)

    def test_fails_closed_when_context_is_missing(self) -> None:
        decision = self.guardian.evaluate(Action("move_base", {"speed_mps": 0.2}), {})
        self.assertEqual(decision.outcome, Outcome.DENY)
        self.assertTrue(any(reason.startswith("missing_context") for reason in decision.reasons))

    def test_high_force_requires_approval(self) -> None:
        decision = self.guardian.evaluate(
            Action("grasp", {"force_n": 30}), {"estop": False}
        )
        self.assertEqual(decision.outcome, Outcome.REQUIRE_APPROVAL)

    def test_estop_denies_every_action(self) -> None:
        decision = self.guardian.evaluate(Action("grasp", {"force_n": 5}), {"estop": True})
        self.assertEqual(decision.outcome, Outcome.DENY)
        self.assertIn("emergency_stop", decision.reasons)

    def test_malformed_parameters_fail_closed(self) -> None:
        decision = self.guardian.evaluate(
            Action("move_base", {"speed_mps": "fast"}),
            {"estop": False, "human_distance_m": 3.0},
        )
        self.assertEqual(decision.outcome, Outcome.DENY)
        self.assertTrue(any(r.startswith("rule_error:") for r in decision.reasons))

    def test_nan_sensor_reading_is_denied(self) -> None:
        decision = self.guardian.evaluate(
            Action("move_base", {"speed_mps": 0.3}),
            {"estop": False, "human_distance_m": float("nan")},
        )
        self.assertEqual(decision.outcome, Outcome.DENY)

    def test_audit_log_is_sequenced(self) -> None:
        for _ in range(3):
            self.guardian.evaluate(Action("observe"), {"estop": False})
        self.assertEqual([d.sequence for d in self.guardian.audit_log], [1, 2, 3])


if __name__ == "__main__":
    unittest.main()
