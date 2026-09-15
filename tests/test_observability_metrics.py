import unittest

from jarvis.observability import MetricDefinition, MetricKind, MetricRegistry


class ObservabilityMetricsTests(unittest.TestCase):
    def test_counter_accumulates_by_label_set(self):
        registry = MetricRegistry()
        registry.register(MetricDefinition("tasks.completed", MetricKind.COUNTER))
        registry.increment("tasks.completed", labels={"component": "orchestrator"})
        registry.increment("tasks.completed", 2, labels={"component": "orchestrator"})
        registry.increment("tasks.completed", labels={"component": "worker"})

        snapshots = registry.snapshot("tasks.completed")
        self.assertEqual(len(snapshots), 2)
        values = {dict(item.labels)["component"]: item.value for item in snapshots}
        self.assertEqual(values["orchestrator"], 3.0)
        self.assertEqual(values["worker"], 1.0)

    def test_gauge_keeps_latest_value(self):
        registry = MetricRegistry()
        registry.register(MetricDefinition("active.agents", MetricKind.GAUGE))
        registry.set_gauge("active.agents", 4)
        registry.set_gauge("active.agents", 7)

        snapshot = registry.snapshot("active.agents")[0]
        self.assertEqual(snapshot.value, 7.0)

    def test_histogram_exposes_basic_statistics(self):
        registry = MetricRegistry()
        registry.register(MetricDefinition("task.duration", MetricKind.HISTOGRAM, unit="ms"))
        for value in (10, 20, 30):
            registry.observe("task.duration", value)

        snapshot = registry.snapshot("task.duration")[0]
        self.assertEqual(snapshot.count, 3)
        self.assertEqual(snapshot.total, 60.0)
        self.assertEqual(snapshot.value, 20.0)
        self.assertEqual(snapshot.minimum, 10.0)
        self.assertEqual(snapshot.maximum, 30.0)

    def test_invalid_metric_operations_are_rejected(self):
        registry = MetricRegistry()
        registry.register(MetricDefinition("requests", MetricKind.COUNTER))
        with self.assertRaises(ValueError):
            registry.increment("requests", -1)
        with self.assertRaises(TypeError):
            registry.set_gauge("requests", 1)
        with self.assertRaises(KeyError):
            registry.increment("unknown")

    def test_duplicate_definition_must_match(self):
        registry = MetricRegistry()
        definition = MetricDefinition("requests", MetricKind.COUNTER)
        registry.register(definition)
        registry.register(definition)
        with self.assertRaises(ValueError):
            registry.register(MetricDefinition("requests", MetricKind.GAUGE))

    def test_invalid_labels_and_non_finite_values_are_rejected(self):
        registry = MetricRegistry()
        registry.register(MetricDefinition("requests", MetricKind.COUNTER))
        with self.assertRaises(ValueError):
            registry.increment("requests", labels={"": "value"})
        with self.assertRaises(ValueError):
            registry.increment("requests", float("nan"))


if __name__ == "__main__":
    unittest.main()
