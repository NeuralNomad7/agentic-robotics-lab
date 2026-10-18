import unittest

from agentic_robotics.world_memory import WorldMemory


class WorldMemoryTests(unittest.TestCase):
    def test_newer_observation_can_replace_stale_belief(self) -> None:
        memory = WorldMemory(half_life_seconds=10)
        memory.observe("mug", "table", confidence=0.99, source="camera-a", observed_at=0)
        memory.observe("mug", "sink", confidence=0.80, source="camera-b", observed_at=20)
        belief = memory.recall("mug", now=20)
        self.assertIsNotNone(belief)
        self.assertEqual(belief.value, "sink")

    def test_location_scopes_recall(self) -> None:
        memory = WorldMemory()
        memory.observe("cart", "empty", confidence=0.8, source="cam", location="west", observed_at=1)
        self.assertIsNone(memory.recall("cart", location="east", now=1))

    def test_contradiction_supersedes_a_more_confident_older_report(self) -> None:
        memory = WorldMemory()
        memory.observe("mug", "on_table", confidence=0.92, source="wrist", observed_at=100)
        memory.observe("mug", "in_sink", confidence=0.81, source="overhead", observed_at=101)
        belief = memory.recall("mug", now=101)
        self.assertEqual(belief.value, "in_sink")
        self.assertEqual(len(memory.observations), 2)  # audit trail is kept

    def test_repeated_agreement_outweighs_one_contradiction(self) -> None:
        memory = WorldMemory()
        for t in (100, 101, 102):
            memory.observe("door", "closed", confidence=0.9, source="cam", observed_at=t)
        memory.observe("door", "open", confidence=0.3, source="noisy", observed_at=103)
        belief = memory.recall("door", now=103)
        self.assertEqual(belief.value, "closed")
        self.assertEqual(belief.supporting_observations, 3)

    def test_rejects_invalid_confidence(self) -> None:
        with self.assertRaises(ValueError):
            WorldMemory().observe("x", "y", confidence=1.5, source="cam")


if __name__ == "__main__":
    unittest.main()
