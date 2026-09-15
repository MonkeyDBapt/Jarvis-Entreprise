import unittest

from jarvis.core import AutonomyEvaluator, AutonomyLevel, AutonomyPolicy


class AutonomyLevelTests(unittest.TestCase):
    def test_levels_are_ordered(self):
        self.assertLess(AutonomyLevel.NONE, AutonomyLevel.ASSISTED)
        self.assertLess(AutonomyLevel.ASSISTED, AutonomyLevel.SUPERVISED)
        self.assertLess(AutonomyLevel.SUPERVISED, AutonomyLevel.BOUNDED)
        self.assertLess(AutonomyLevel.BOUNDED, AutonomyLevel.DELEGATED)

    def test_lower_levels_require_approval(self):
        for level in (AutonomyLevel.NONE, AutonomyLevel.ASSISTED, AutonomyLevel.SUPERVISED):
            with self.subTest(level=level):
                policy = AutonomyPolicy("agent-1", level)
                self.assertTrue(AutonomyEvaluator.requires_approval(policy))
                self.assertFalse(AutonomyEvaluator.can_act_without_approval(policy))

    def test_bounded_and_delegated_levels_can_act_without_approval(self):
        for level in (AutonomyLevel.BOUNDED, AutonomyLevel.DELEGATED):
            with self.subTest(level=level):
                policy = AutonomyPolicy("agent-1", level)
                self.assertFalse(AutonomyEvaluator.requires_approval(policy))
                self.assertTrue(AutonomyEvaluator.can_act_without_approval(policy))

    def test_policy_rejects_invalid_subject(self):
        with self.assertRaises(ValueError):
            AutonomyPolicy("", AutonomyLevel.ASSISTED)

    def test_policy_rejects_invalid_level(self):
        with self.assertRaises(TypeError):
            AutonomyPolicy("agent-1", 3)

    def test_policy_is_independent_from_permissions(self):
        policy = AutonomyPolicy("agent-1", AutonomyLevel.BOUNDED)
        self.assertTrue(AutonomyEvaluator.can_act_without_approval(policy))
        # Permission authorization is intentionally evaluated by Phase 8.4,
        # not granted by the autonomy layer.


if __name__ == "__main__":
    unittest.main()
