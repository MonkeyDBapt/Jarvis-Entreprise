import asyncio
import unittest

from jarvis.communication import (
    ChannelKind,
    CommunicationMessage,
    InMemoryMessageDelivery,
    CommunicationRouter,
)
from jarvis.orchestrator import JarvisOrchestrator, OrchestrationRequest
from jarvis.core.security import SecurityController


class StubOrchestrator(JarvisOrchestrator):
    async def run(self, request: OrchestrationRequest) -> str:
        return f"processed:{request.message}"


class OrchestratorCommunicationTests(unittest.TestCase):
    def test_orchestrator_routes_response_through_communication_boundary(self) -> None:
        delivery = InMemoryMessageDelivery()
        received: list[CommunicationMessage] = []
        delivery.register("client", received.append)

        security = SecurityController()
        security.allow("jarvis", "send", "communication:client")
        router = CommunicationRouter(
            message_delivery=delivery,
            security_controller=security,
        )
        orchestrator = StubOrchestrator(communication_router=router)

        request = OrchestrationRequest(
            message="hello",
            session_id="session-1",
            task_id="task-1",
        )
        response = asyncio.run(
            orchestrator.run_and_reply(
                request,
                sender_id="jarvis",
                recipient_id="client",
                correlation_id="request-1",
                channel=ChannelKind.MESSAGE,
            )
        )

        self.assertEqual(received, [response])
        self.assertEqual(response.sender_id, "jarvis")
        self.assertEqual(response.recipient_id, "client")
        self.assertEqual(response.payload, {"response": "processed:hello"})
        self.assertEqual(response.correlation_id, "request-1")
        self.assertEqual(response.session_id, "session-1")
        self.assertEqual(response.task_id, "task-1")

    def test_orchestrator_fails_without_communication_configuration(self) -> None:
        orchestrator = StubOrchestrator()

        with self.assertRaises(RuntimeError):
            asyncio.run(
                orchestrator.run_and_reply(
                    OrchestrationRequest(message="hello"),
                    sender_id="jarvis",
                    recipient_id="client",
                )
            )

    def test_communication_security_is_preserved_by_orchestrator(self) -> None:
        delivery = InMemoryMessageDelivery()
        received: list[CommunicationMessage] = []
        delivery.register("client", received.append)
        router = CommunicationRouter(
            message_delivery=delivery,
            security_controller=SecurityController(),
        )
        orchestrator = StubOrchestrator(communication_router=router)

        with self.assertRaises(PermissionError):
            asyncio.run(
                orchestrator.run_and_reply(
                    OrchestrationRequest(message="hello"),
                    sender_id="jarvis",
                    recipient_id="client",
                )
            )

        self.assertEqual(received, [])


if __name__ == "__main__":
    unittest.main()
