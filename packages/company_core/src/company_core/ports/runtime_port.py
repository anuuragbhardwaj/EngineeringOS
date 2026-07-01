"""Runtime port — contract surface for ProjectAPI (no runtime_engine imports)."""

from __future__ import annotations

from typing import Any, Protocol


class IRuntimePort(Protocol):
    """Minimum Runtime facade contract consumed by Framework API."""

    def init_project(
        self,
        project_id: str,
        artifact_root: str | None = None,
        metadata: dict | None = None,
    ) -> Any: ...

    def execute_planning_pipeline(
        self,
        project_id: str,
        stop_after_phase: str = "architecture",
    ) -> Any: ...

    def status(self, project_id: str) -> Any: ...

    def load_project(self, project_id: str) -> Any: ...

    def history(self, project_id: str) -> dict: ...

    def validate(self, project_id: str) -> Any: ...

    def list_project_ids(self) -> list[str]: ...

    def project_exists(self, project_id: str) -> bool: ...
