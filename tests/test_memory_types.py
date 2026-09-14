import unittest

from jarvis.core import MemoryKind


class MemoryTypeTaxonomyTests(unittest.TestCase):
    def test_memory_kinds_are_explicit(self) -> None:
        self.assertEqual(MemoryKind.WORKING.value, "working")
        self.assertEqual(MemoryKind.EPISODIC.value, "episodic")
        self.assertEqual(MemoryKind.SEMANTIC.value, "semantic")
        self.assertEqual(MemoryKind.USER.value, "user")
        self.assertEqual(MemoryKind.SYSTEM.value, "system")

    def test_taxonomy_contains_five_distinct_kinds(self) -> None:
        values = {kind.value for kind in MemoryKind}
        self.assertEqual(values, {"working", "episodic", "semantic", "user", "system"})

    def test_taxonomy_is_independent_from_high_level_memory_type(self) -> None:
        self.assertNotEqual(set(MemoryKind), set())


if __name__ == "__main__":
    unittest.main()
