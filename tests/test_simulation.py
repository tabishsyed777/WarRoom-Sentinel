import unittest

from war_room.orchestrator import run


class SimulationTests(unittest.TestCase):
    def test_simulation_produces_terminal_outcome_and_replay(self) -> None:
        report = run(seed=7, max_turns=12)
        self.assertIn(report["outcome"], {"attacker_win", "defender_win"})
        self.assertTrue(report["replay"])
        self.assertLessEqual(report["turns"], 12)


    def test_report_is_deterministic_for_a_seed(self) -> None:
        self.assertEqual(run(seed=21, max_turns=8), run(seed=21, max_turns=8))
