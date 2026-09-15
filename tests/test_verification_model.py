import unittest

from jarvis.verification import (
    VerificationCheck,
    VerificationReport,
    VerificationSeverity,
    VerificationStatus,
)


class VerificationModelTests(unittest.TestCase):
    def test_passed_report_requires_all_checks_to_pass(self):
        report = VerificationReport(
            id="report-1",
            scope="phase-9.1",
            checks=(
                VerificationCheck(
                    id="check-1",
                    name="contract",
                    target="orchestrator",
                    category="architecture",
                    status=VerificationStatus.PASSED,
                    expected="stable contract",
                    observed="stable contract",
                ),
                VerificationCheck(
                    id="check-2",
                    name="integration",
                    target="runtime",
                    category="integration",
                    status=VerificationStatus.PASSED,
                ),
            ),
        )

        self.assertEqual(report.status, VerificationStatus.PASSED)
        self.assertTrue(report.passed)

    def test_failure_is_terminal_for_report_status(self):
        report = VerificationReport(
            id="report-2",
            scope="phase-9.1",
            checks=(
                VerificationCheck(
                    id="check-1",
                    name="failed-check",
                    target="component",
                    category="functional",
                    status=VerificationStatus.FAILED,
                    severity=VerificationSeverity.ERROR,
                ),
                VerificationCheck(
                    id="check-2",
                    name="passed-check",
                    target="component",
                    category="functional",
                    status=VerificationStatus.PASSED,
                ),
            ),
        )

        self.assertEqual(report.status, VerificationStatus.FAILED)
        self.assertFalse(report.passed)

    def test_inconclusive_is_not_reported_as_passed(self):
        report = VerificationReport(
            id="report-3",
            scope="phase-9.1",
            checks=(
                VerificationCheck(
                    id="check-1",
                    name="unknown",
                    target="component",
                    category="functional",
                    status=VerificationStatus.INCONCLUSIVE,
                ),
            ),
        )

        self.assertEqual(report.status, VerificationStatus.INCONCLUSIVE)
        self.assertFalse(report.passed)

    def test_duplicate_check_ids_are_rejected(self):
        check = VerificationCheck(
            id="duplicate",
            name="check",
            target="component",
            category="functional",
            status=VerificationStatus.PASSED,
        )

        with self.assertRaises(ValueError):
            VerificationReport(
                id="report-4",
                scope="phase-9.1",
                checks=(check, check),
            )

    def test_empty_identity_fields_are_rejected(self):
        with self.assertRaises(ValueError):
            VerificationCheck(
                id="",
                name="check",
                target="component",
                category="functional",
                status=VerificationStatus.PASSED,
            )


if __name__ == "__main__":
    unittest.main()
