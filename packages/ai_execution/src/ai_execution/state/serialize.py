"""Conversation persistence."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from ai_execution.types import Conversation, Message, MessageRole


def conversation_to_dict(conv: Conversation) -> dict:
    return {
        "conversation_id": conv.conversation_id,
        "session_id": conv.session_id,
        "employee_id": conv.employee_id,
        "project_id": conv.project_id,
        "created_at": conv.created_at.isoformat(),
        "updated_at": conv.updated_at.isoformat(),
        "metadata": conv.metadata,
        "messages": [
            {
                "role": m.role.value,
                "content": m.content,
                "timestamp": m.timestamp.isoformat(),
            }
            for m in conv.messages
        ],
    }


def conversation_from_dict(data: dict) -> Conversation:
    return Conversation(
        conversation_id=data["conversation_id"],
        session_id=data.get("session_id", ""),
        employee_id=data["employee_id"],
        project_id=data["project_id"],
        messages=[
            Message(
                role=MessageRole(m["role"]),
                content=m["content"],
                timestamp=datetime.fromisoformat(m["timestamp"]),
            )
            for m in data.get("messages", [])
        ],
        created_at=datetime.fromisoformat(data["created_at"]),
        updated_at=datetime.fromisoformat(data["updated_at"]),
        metadata=dict(data.get("metadata", {})),
    )


def save_conversation(path: Path, conversation: Conversation) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(conversation_to_dict(conversation), indent=2), encoding="utf-8")
    temp.replace(path)


def load_conversation(path: Path) -> Conversation:
    data = json.loads(path.read_text(encoding="utf-8"))
    return conversation_from_dict(data)
