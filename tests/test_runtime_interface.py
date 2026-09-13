"""Tests for the stable JARVIS runtime interface boundary."""

from __future__ import annotations

import unittest

from jarvis.interfaces import AgentRuntime
from jarvis.runtime import HermesAdapter


class RuntimeInterfaceTests(unittest.TestCase):
    def test_hermes_adapter_conforms_to_runtime_interface(self) -> None:
        runtime = HermesAdapter()
        self.assertIsInstance(runtime, AgentRuntime)


if __name__ == "__main__":
    unittest.main()
