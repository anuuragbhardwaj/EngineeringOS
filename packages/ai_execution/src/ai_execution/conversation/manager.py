"""Conversation lifecycle management."""

from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path

from ai_execution.errors import ConversationCorruptError
from ai_execution.state.serialize import load_conversation, save_conversation
from ai_execution.types import Conversation, ExecutionSession, Message, MessageRole


class ConversationManager:
    """Manages conversation IDs, sessions, history, and persistence."""

    def __init__(self, storage_root: Path | None = None) -> None:
        self._storage_root = storage_root
        self._conversations: dict[str, Conversation] = {}
        self._sessions: dict[str, ExecutionSession] = {}

    def set_storage_root(self, project_root: Path) -> None:
        self._storage_root = project_root / ".runtime" / "conversations"

    def create_session(
        self,
        project_id: str,
        employee_id: str,
        phase_id: str,
    ) -> ExecutionSession:
        session_id = str(uuid.uuid4())
        conversation = self.create_conversation(project_id, employee_id)
        session = ExecutionSession(
            session_id=session_id,
            project_id=project_id,
            employee_id=employee_id,
            phase_id=phase_id,
            conversation_id=conversation.conversation_id,
        )
        self._sessions[session_id] = session
        return session

    def create_conversation(self, project_id: str, employee_id: str) -> Conversation:
        conversation_id = str(uuid.uuid4())
        conversation = Conversation(
            conversation_id=conversation_id,
            session_id="",
            employee_id=employee_id,
            project_id=project_id,
        )
        self._conversations[conversation_id] = conversation
        return conversation

    def get_conversation(self, conversation_id: str) -> Conversation:
        if conversation_id in self._conversations:
            return self._conversations[conversation_id]
        if self._storage_root:
            path = self._storage_root / f"{conversation_id}.json"
            if path.is_file():
                conv = load_conversation(path)
                self._conversations[conversation_id] = conv
                return conv
        raise ConversationCorruptError(f"Conversation not found: {conversation_id}")

    def append_message(
        self,
        conversation_id: str,
        role: MessageRole,
        content: str,
    ) -> None:
        conversation = self.get_conversation(conversation_id)
        conversation.messages.append(Message(role=role, content=content))
        conversation.updated_at = datetime.utcnow()
        self._persist(conversation)

    def add_system_prompt(self, conversation_id: str, prompt: str) -> None:
        self.append_message(conversation_id, MessageRole.SYSTEM, prompt)

    def add_user_context(self, conversation_id: str, context: str) -> None:
        self.append_message(conversation_id, MessageRole.USER, context)

    def add_assistant_response(self, conversation_id: str, response: str) -> None:
        self.append_message(conversation_id, MessageRole.ASSISTANT, response)

    def get_history(self, conversation_id: str) -> list[Message]:
        return list(self.get_conversation(conversation_id).messages)

    def end_session(self, session_id: str, provider_id: str | None = None) -> None:
        session = self._sessions.get(session_id)
        if session:
            session.ended_at = datetime.utcnow()
            session.provider_id = provider_id

    def _persist(self, conversation: Conversation) -> None:
        if self._storage_root is None:
            return
        self._storage_root.mkdir(parents=True, exist_ok=True)
        save_conversation(self._storage_root / f"{conversation.conversation_id}.json", conversation)
