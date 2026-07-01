"""Conversation routing — provider-independent lifecycle."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field


@dataclass
class ConversationRoute:
    route_key: str
    conversation_id: str
    branch: str = "main"
    archived: bool = False
    metadata: dict = field(default_factory=dict)


class ConversationRouter:
    """Owns conversation reuse, reset, archive, and branching."""

    def __init__(self) -> None:
        self._routes: dict[str, ConversationRoute] = {}

    def route_key(self, project_id: str, employee_id: str, phase_id: str) -> str:
        return f"{project_id}:{employee_id}:{phase_id}"

    def resolve(
        self,
        project_id: str,
        employee_id: str,
        phase_id: str,
        *,
        reuse: bool = True,
    ) -> str:
        key = self.route_key(project_id, employee_id, phase_id)
        if reuse and key in self._routes and not self._routes[key].archived:
            return self._routes[key].conversation_id

        conversation_id = str(uuid.uuid4())
        self._routes[key] = ConversationRoute(route_key=key, conversation_id=conversation_id)
        return conversation_id

    def reset(self, project_id: str, employee_id: str, phase_id: str) -> str:
        key = self.route_key(project_id, employee_id, phase_id)
        conversation_id = str(uuid.uuid4())
        self._routes[key] = ConversationRoute(route_key=key, conversation_id=conversation_id)
        return conversation_id

    def archive(self, project_id: str, employee_id: str, phase_id: str) -> None:
        key = self.route_key(project_id, employee_id, phase_id)
        if key in self._routes:
            self._routes[key].archived = True

    def branch(self, project_id: str, employee_id: str, phase_id: str, branch: str) -> str:
        key = f"{self.route_key(project_id, employee_id, phase_id)}:{branch}"
        conversation_id = str(uuid.uuid4())
        self._routes[key] = ConversationRoute(
            route_key=key, conversation_id=conversation_id, branch=branch
        )
        return conversation_id
