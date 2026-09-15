import unittest

from jarvis.observability import (
    HealthCheck,
    HealthCheckResult,
    HealthRegistry,
    HealthStatus,
    SystemHealth,
)


class SystemHealthTests(unittest.TestCase):
    def test_empty_registry_is_unknown(self) -> None:
        health = HealthRegistry().snapshot()
        self.assertIsInstance(health, SystemHealth)
        self.assertIs(health.status, HealthStatus.UNKNOWN)
        self.assertFalse(health.healthy)

    def test_register_record_and_snapshot(self) -> None:
        registry = HealthRegistry()
        registry.register(HealthCheck("runtime", "agent-runtime", critical=True))
        registry.record(
            HealthCheckResult(
                "runtime", "agent-runtime", HealthStatus.HEALTHY, message="ready", critical=True
            )
        )

        health = registry.snapshot()
        self.assertIs(health.status, HealthStatus.HEALTHY)
        self.assertTrue(health.healthy)
        self.assertEqual(health.checks[0].name, "runtime")
        self.assertEqual(health.as_dict()["status"], "healthy")

    def test_critical_unhealthy_check_makes_system_unhealthy(self) -> None:
        registry = HealthRegistry()
        registry.register(HealthCheck("runtime", "agent-runtime", critical=True))
        registry.record(HealthCheckResult("runtime", "agent-runtime", HealthStatus.UNHEALTHY, critical=True))

        self.assertIs(registry.snapshot().status, HealthStatus.UNHEALTHY)

    def test_non_critical_unhealthy_check_degrades_system(self) -> None:
        registry = HealthRegistry()
        registry.register(HealthCheck("provider", "model-provider"))
        registry.record(HealthCheckResult("provider", "model-provider", HealthStatus.UNHEALTHY))

        self.assertIs(registry.snapshot().status, HealthStatus.DEGRADED)

    def test_run_all_records_sorted_checks(self) -> None:
        registry = HealthRegistry()
        registry.register(HealthCheck("z-runtime", "runtime"))
        registry.register(HealthCheck("a-runtime", "runtime"))

        def evaluator(check: HealthCheck) -> HealthCheckResult:
            return HealthCheckResult(check.name, check.component, HealthStatus.HEALTHY, critical=check.critical)

        health = registry.run_all(evaluator)
        self.assertEqual([check.name for check in health.checks], ["a-runtime", "z-runtime"])
        self.assertIs(health.status, HealthStatus.HEALTHY)

    def test_invalid_result_cannot_bypass_registered_contract(self) -> None:
        registry = HealthRegistry()
        registry.register(HealthCheck("runtime", "agent-runtime", critical=True))

        with self.assertRaises(KeyError):
            registry.record(HealthCheckResult("missing", "agent-runtime", HealthStatus.HEALTHY))
        with self.assertRaises(ValueError):
            registry.record(HealthCheckResult("runtime", "other", HealthStatus.HEALTHY, critical=True))
        with self.assertRaises(ValueError):
            registry.record(HealthCheckResult("runtime", "agent-runtime", HealthStatus.HEALTHY, critical=False))


if __name__ == "__main__":
    unittest.main()
