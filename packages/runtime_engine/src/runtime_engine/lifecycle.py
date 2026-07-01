"""Runtime lifecycle bridge — Orchestrator delegates persistence and gates to Runtime."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from orchestrator.types import LifecycleCallbacks

from runtime_engine.state.mutator import PipelineStateMutator

if TYPE_CHECKING:
    from runtime_engine.runtime.facade import Runtime


class RuntimeLifecycleBridge(LifecycleCallbacks):
    """Thin adapter so Orchestrator never persists or validates directly."""

    def __init__(self, runtime: Runtime, project_id: str) -> None:
        self._runtime = runtime
        self._project_id = project_id
        self._state: Any = None
        self._mutator: PipelineStateMutator | None = None

    def bind(self, state: Any) -> None:
        self._state = state
        self._mutator = PipelineStateMutator(state)

    @property
    def state(self) -> Any:
        return self._state

    @property
    def mutator(self) -> PipelineStateMutator:
        if self._mutator is None:
            raise RuntimeError("Lifecycle bridge not bound to state")
        return self._mutator

    def persist(self, state: Any) -> None:
        self._state = state
        self._runtime._persist(self._project_id, state)  # noqa: SLF001

    def validate(self) -> Any:
        return self._runtime._validation.validate_phase_exit(  # noqa: SLF001
            self._state, self._runtime._workflow  # noqa: SLF001
        )

    def evaluate_gate(self) -> Any:
        return self._runtime._gate.evaluate(self._state, self._runtime._workflow)  # noqa: SLF001

    def record_gate(self, gate_id: str, passed: bool, notes: str) -> None:
        self._state, _record = self._runtime._gate.record_result(  # noqa: SLF001
            self._state, gate_id, passed, notes, "em", False
        )
        self._runtime._persist(self._project_id, self._state)  # noqa: SLF001
        from runtime_engine.events import catalog as events

        event = events.GatePassed if passed else events.GateRejected
        self._runtime._bus.publish(  # noqa: SLF001
            self._runtime._bus.make_event(  # noqa: SLF001
                event,
                self._project_id,
                {"gate_id": gate_id, "phase_id": _record.phase_id, "evaluator": "em", "notes": notes},
            )
        )

    def advance(self) -> Any:
        from runtime_engine.errors import TransitionError
        from runtime_engine.events import catalog as events

        previous = self._state.current_phase_id
        try:
            self._state = self._runtime._pipeline.advance(  # noqa: SLF001
                self._state, self._runtime._workflow  # noqa: SLF001
            )
        except TransitionError as exc:
            self._runtime._bus.publish(  # noqa: SLF001
                self._runtime._bus.make_event(
                    events.TransitionBlocked,
                    self._project_id,
                    {"target_phase_id": None, "reason": str(exc), "blockers": [str(exc)]},
                )
            )
            raise
        self._runtime._persist(self._project_id, self._state)  # noqa: SLF001
        self._runtime._bus.publish(  # noqa: SLF001
            self._runtime._bus.make_event(
                events.PhaseCompleted,
                self._project_id,
                {"phase_id": previous, "gate_id": None},
            )
        )
        self._runtime._bus.publish(  # noqa: SLF001
            self._runtime._bus.make_event(
                events.PhaseEntered,
                self._project_id,
                {"phase_id": self._state.current_phase_id, "previous_phase_id": previous},
            )
        )
        return self._state

    def publish_event(self, event_type: str, payload: dict) -> None:
        self._runtime._bus.publish(  # noqa: SLF001
            self._runtime._bus.make_event(event_type, self._project_id, payload)
        )

    def is_approved(self, gate_id: str) -> bool:
        return self._runtime._orchestrator.approval_hooks.is_approved(  # noqa: SLF001
            self._runtime._orchestrator.approval_hooks.approval_key(  # noqa: SLF001
                self._project_id, gate_id
            )
        )
