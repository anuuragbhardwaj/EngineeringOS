"""In-process event bus."""

from __future__ import annotations

import logging
import uuid
from collections import defaultdict
from collections.abc import Callable
from datetime import datetime

from runtime_engine.version import CONTRACT_VERSION
from runtime_engine.types import KernelEvent, ProjectId, SubscriptionId

logger = logging.getLogger(__name__)


class EventBus:
    """IEventBus implementation."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[tuple[SubscriptionId, Callable[[KernelEvent], None]]]] = (
            defaultdict(list)
        )
        self._all_handlers: list[tuple[SubscriptionId, Callable[[KernelEvent], None]]] = []

    def publish(self, event: KernelEvent) -> None:
        handlers = list(self._handlers.get(event.type, []))
        handlers.extend(self._all_handlers)
        for _sub_id, handler in handlers:
            try:
                handler(event)
            except Exception as exc:
                logger.exception("Event handler failed: %s", exc)
                self._emit_handler_failed(event, exc)

    def subscribe(
        self,
        event_type: str,
        handler: Callable[[KernelEvent], None],
    ) -> SubscriptionId:
        sub_id = str(uuid.uuid4())
        self._handlers[event_type].append((sub_id, handler))
        return sub_id

    def unsubscribe(self, subscription_id: SubscriptionId) -> None:
        for event_type, handlers in self._handlers.items():
            self._handlers[event_type] = [
                (sid, h) for sid, h in handlers if sid != subscription_id
            ]
        self._all_handlers = [
            (sid, h) for sid, h in self._all_handlers if sid != subscription_id
        ]

    def subscribe_all(
        self,
        handler: Callable[[KernelEvent], None],
    ) -> SubscriptionId:
        sub_id = str(uuid.uuid4())
        self._all_handlers.append((sub_id, handler))
        return sub_id

    def make_event(
        self,
        event_type: str,
        project_id: ProjectId,
        payload: dict,
        correlation_id: str | None = None,
    ) -> KernelEvent:
        return KernelEvent(
            type=event_type,
            project_id=project_id,
            timestamp=datetime.utcnow(),
            contract_version=CONTRACT_VERSION,
            payload=payload,
            correlation_id=correlation_id,
        )

    def _emit_handler_failed(self, event: KernelEvent, exc: Exception) -> None:
        failure = self.make_event(
            "PluginHandlerFailed",
            event.project_id,
            {
                "plugin_id": "handler",
                "event_type": event.type,
                "error": str(exc),
            },
        )
        for _sub_id, handler in self._all_handlers:
            try:
                handler(failure)
            except Exception:
                logger.exception("PluginHandlerFailed handler also failed")
