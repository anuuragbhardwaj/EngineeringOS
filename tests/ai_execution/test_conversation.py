"""Conversation lifecycle tests."""

from pathlib import Path

from ai_execution.conversation.manager import ConversationManager
from ai_execution.types import MessageRole


def test_conversation_lifecycle(tmp_path: Path) -> None:
    mgr = ConversationManager()
    mgr.set_storage_root(tmp_path)

    session = mgr.create_session("proj-1", "senior-product-manager", "requirements")
    mgr.add_system_prompt(session.conversation_id, "You are the PM.")
    mgr.add_user_context(session.conversation_id, "Write requirements.md")
    mgr.add_assistant_response(session.conversation_id, "Done.")

    history = mgr.get_history(session.conversation_id)
    assert len(history) == 3
    assert history[0].role == MessageRole.SYSTEM

    persisted = tmp_path / ".runtime" / "conversations" / f"{session.conversation_id}.json"
    assert persisted.is_file()
