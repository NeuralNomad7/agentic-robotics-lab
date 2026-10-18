import unittest

from agentic_robotics.fleetmind import FleetCoordinator, Robot, Task


class FleetMindTests(unittest.TestCase):
    def test_reassigns_after_heartbeat_timeout(self) -> None:
        fleet = FleetCoordinator(heartbeat_timeout=5)
        fleet.register(Robot("near", frozenset({"carry"}), (0, 0), 0.9, last_heartbeat=0))
        fleet.register(Robot("far", frozenset({"carry"}), (5, 0), 0.9, last_heartbeat=0))
        task = Task("t1", "carry", (1, 0))
        first = fleet.allocate(task, now=1)
        self.assertEqual(first.robot_id, "near")

        fleet.heartbeat("far", now=10)
        second = fleet.allocate(task, now=10)
        self.assertEqual(second.robot_id, "far")

    def test_respects_capabilities(self) -> None:
        fleet = FleetCoordinator()
        fleet.register(Robot("camera", frozenset({"inspect"}), (0, 0), 1.0, last_heartbeat=0))
        self.assertIsNone(fleet.allocate(Task("t2", "weld", (0, 0)), now=1))

    def test_load_is_tracked_and_spreads_work(self) -> None:
        fleet = FleetCoordinator()
        fleet.register(Robot("a", frozenset({"carry"}), (0, 0), 0.9, last_heartbeat=0))
        fleet.register(Robot("b", frozenset({"carry"}), (0.5, 0), 0.9, last_heartbeat=0))
        first = fleet.allocate(Task("t1", "carry", (0, 0)), now=1)
        second = fleet.allocate(Task("t2", "carry", (0, 0)), now=1)
        self.assertEqual(first.robot_id, "a")
        self.assertEqual(second.robot_id, "b")  # "a" is now busier
        fleet.release("t1")
        self.assertEqual(fleet.robots["a"].active_tasks, 0)

    def test_reassignment_moves_the_load(self) -> None:
        fleet = FleetCoordinator(heartbeat_timeout=5)
        fleet.register(Robot("near", frozenset({"carry"}), (0, 0), 0.9, last_heartbeat=0))
        fleet.register(Robot("far", frozenset({"carry"}), (5, 0), 0.9, last_heartbeat=0))
        task = Task("t1", "carry", (1, 0))
        fleet.allocate(task, now=1)
        fleet.heartbeat("far", now=10)
        fleet.allocate(task, now=10)
        self.assertEqual(fleet.robots["near"].active_tasks, 0)
        self.assertEqual(fleet.robots["far"].active_tasks, 1)

    def test_low_battery_robot_is_skipped(self) -> None:
        fleet = FleetCoordinator()
        fleet.register(Robot("tired", frozenset({"carry"}), (0, 0), 0.05, last_heartbeat=0))
        self.assertIsNone(fleet.allocate(Task("t1", "carry", (0, 0)), now=1))


if __name__ == "__main__":
    unittest.main()
