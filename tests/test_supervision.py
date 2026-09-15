import unittest
from datetime import datetime, timezone, timedelta

from jarvis.core import (
    AutonomyLevel,
    AutonomyPolicy,
    AuthorizationDecision,
    AuthorizationRequest,
    ControlEvaluator,
    ControlOutcome,
    SupervisionEvaluator,
    SupervisionOutcome,
    SupervisionPolicy,
)


class SupervisionEvaluatorTests(unittest.TestCase):
    def authorization(self, allowed: bool = True) -> AuthorizationDecision:
        request = AuthorizationRequest(
            subject_id="agent-1",
            action="execute",
            resource="capability:search",
            scope="agent:agent-1",
        )
        return AuthorizationDecision(allowed=allowed, request=request)

    def control(self, autonomy=AutonomyLevel.BOUNDED):
        return ControlEvaluator.evaluate(
            self.authorization(True), AutonomyPolicy("agent-1", autonomy)
        )

    def test_denied_authorization_remains_terminal(self):
        control = ControlEvaluator.evaluate(self.authorization(False), AutonomyPolicy("agent-1", AutonomyLevel.DELEGATED))
        decision = SupervisionEvaluator.evaluate(control)
        self.assertEqual(decision.outcome, SupervisionOutcome.DENIED)
        self.assertFalse(decision.allowed)

    def test_revocation_blocks_authorized_action(self):
        decision = SupervisionEvaluator.evaluate(
            self.control(), SupervisionPolicy("agent-1", revoked=True)
        )
        self.assertEqual(decision.outcome, SupervisionOutcome.REVOKED)
        self.assertFalse(decision.allowed)

    def test_action_restriction_blocks_action(self):
        policy = SupervisionPolicy("agent-1", allowed_actions=frozenset({"read"}))
        decision = SupervisionEvaluator.evaluate(self.control(), policy)
        self.assertEqual(decision.outcome, SupervisionOutcome.RESTRICTED)

    def test_resource_restriction_blocks_action(self):
        policy = SupervisionPolicy("agent-1", allowed_resources=frozenset({"capability:other"}))
        decision = SupervisionEvaluator.evaluate(self.control(), policy)
        self.assertEqual(decision.outcome, SupervisionOutcome.RESTRICTED)

    def test_expired_policy_blocks_action(self):
        now = datetime(2026, 9, 15, tzinfo=timezone.utc)
        policy = SupervisionPolicy("agent-1", expires_at=now - timedelta(seconds=1))
        decision = SupervisionEvaluator.evaluate(self.control(), policy, now=now)
        self.assertEqual(decision.outcome, SupervisionOutcome.EXPIRED)

    def test_policy_can_require_human_approval(self):
        policy = SupervisionPolicy("agent-1", require_approval=True)
        decision = SupervisionEvaluator.evaluate(self.control(), policy)
        self.assertEqual(decision.outcome, SupervisionOutcome.APPROVAL_REQUIRED)
        self.assertTrue(decision.requires_human_control)
        self.assertFalse(decision.allowed)

    def test_existing_autonomy_control_is_preserved(self):
        control = self.control(AutonomyLevel.SUPERVISED)
        self.assertEqual(control.outcome, ControlOutcome.SUPERVISED)
        decision = SupervisionEvaluator.evaluate(control)
        self.assertEqual(decision.outcome, SupervisionOutcome.APPROVAL_REQUIRED)

    def test_matching_policy_allows_authorized_bounded_action(self):
        policy = SupervisionPolicy(
            "agent-1",
            allowed_actions=frozenset({"execute"}),
            allowed_resources=frozenset({"capability:search"}),
        )
        decision = SupervisionEvaluator.evaluate(self.control(), policy)
        self.assertEqual(decision.outcome, SupervisionOutcome.ALLOWED)
        self.assertTrue(decision.allowed)

    def test_policy_for_another_subject_is_restrictive(self):
        decision = SupervisionEvaluator.evaluate(
            self.control(), SupervisionPolicy("agent-2")
        )
        self.assertEqual(decision.outcome, SupervisionOutcome.RESTRICTED)

    def test_invalid_policy_type_is_rejected(self):
        with self.assertRaises(TypeError):
            SupervisionEvaluator.evaluate(self.control(), object())


if __name__ == "__main__":
    unittest.main()
