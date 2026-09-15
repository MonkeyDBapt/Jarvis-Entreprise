import unittest

from jarvis.core import (
    AutonomyLevel,
    AutonomyPolicy,
    AuthorizationDecision,
    AuthorizationRequest,
    ControlEvaluator,
    ControlOutcome,
)


class ControlEvaluatorTests(unittest.TestCase):
    def authorization(self, allowed: bool) -> AuthorizationDecision:
        request = AuthorizationRequest(
            subject_id="agent-1",
            action="execute",
            resource="capability:search",
            scope="agent:agent-1",
        )
        return AuthorizationDecision(allowed=allowed, request=request)

    def test_denied_authorization_is_always_terminal(self):
        decision = ControlEvaluator.evaluate(
            self.authorization(False),
            AutonomyPolicy("agent-1", AutonomyLevel.DELEGATED),
        )

        self.assertEqual(decision.outcome, ControlOutcome.DENIED)
        self.assertFalse(decision.allowed)
        self.assertTrue(decision.requires_human_control is False)

    def test_missing_autonomy_fails_closed(self):
        decision = ControlEvaluator.evaluate(self.authorization(True))

        self.assertEqual(decision.outcome, ControlOutcome.APPROVAL_REQUIRED)
        self.assertTrue(decision.allowed)
        self.assertTrue(decision.requires_human_control)

    def test_assisted_requires_approval(self):
        decision = ControlEvaluator.evaluate(
            self.authorization(True),
            AutonomyPolicy("agent-1", AutonomyLevel.ASSISTED),
        )

        self.assertEqual(decision.outcome, ControlOutcome.SUPERVISED)
        self.assertTrue(decision.requires_human_control)

    def test_supervised_requires_human_control(self):
        decision = ControlEvaluator.evaluate(
            self.authorization(True),
            AutonomyPolicy("agent-1", AutonomyLevel.SUPERVISED),
        )

        self.assertEqual(decision.outcome, ControlOutcome.SUPERVISED)
        self.assertTrue(decision.requires_human_control)

    def test_bounded_is_autonomous_after_authorization(self):
        decision = ControlEvaluator.evaluate(
            self.authorization(True),
            AutonomyPolicy("agent-1", AutonomyLevel.BOUNDED),
        )

        self.assertEqual(decision.outcome, ControlOutcome.AUTONOMOUS)
        self.assertFalse(decision.requires_human_control)

    def test_delegated_is_autonomous_after_authorization(self):
        decision = ControlEvaluator.evaluate(
            self.authorization(True),
            AutonomyPolicy("agent-1", AutonomyLevel.DELEGATED),
        )

        self.assertEqual(decision.outcome, ControlOutcome.AUTONOMOUS)
        self.assertFalse(decision.requires_human_control)

    def test_invalid_authorization_type_is_rejected(self):
        with self.assertRaises(TypeError):
            ControlEvaluator.evaluate(object())

    def test_invalid_autonomy_type_is_rejected(self):
        with self.assertRaises(TypeError):
            ControlEvaluator.evaluate(self.authorization(True), object())


if __name__ == "__main__":
    unittest.main()
