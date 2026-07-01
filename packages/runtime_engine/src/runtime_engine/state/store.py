"""JSON file state store."""

from __future__ import annotations

from pathlib import Path

from runtime_engine.errors import ProjectNotFoundError, StorageError
from runtime_engine.state.serialize import load_state, save_state
from runtime_engine.types import PipelineState, ProjectId


class JsonStateStore:
    """IStateStore — persists state at {project_root}/.runtime/state.json."""

    def __init__(self, projects_root: Path | None = None) -> None:
        self._projects_root = projects_root
        self._index: dict[ProjectId, Path] = {}

    def register_project_path(self, project_id: ProjectId, project_root: Path) -> None:
        self._index[project_id] = project_root

    def _state_path(self, project_id: ProjectId) -> Path:
        if project_id in self._index:
            return self._index[project_id] / ".runtime" / "state.json"
        if self._projects_root:
            return self._projects_root / project_id / ".runtime" / "state.json"
        raise ProjectNotFoundError(f"Unknown project path for {project_id}")

    def load(self, project_id: ProjectId) -> PipelineState:
        path = self._state_path(project_id)
        if not path.is_file():
            raise ProjectNotFoundError(f"No state for project {project_id}")
        try:
            state = load_state(path)
        except Exception as exc:
            raise StorageError(str(exc)) from exc
        self._index[project_id] = path.parent.parent
        return state

    def save(self, project_id: ProjectId, state: PipelineState) -> None:
        path = self._state_path(project_id)
        try:
            save_state(path, state)
        except OSError as exc:
            raise StorageError(str(exc)) from exc

    def exists(self, project_id: ProjectId) -> bool:
        try:
            return self._state_path(project_id).is_file()
        except ProjectNotFoundError:
            return False

    def delete(self, project_id: ProjectId) -> None:
        path = self._state_path(project_id)
        if path.is_file():
            path.unlink()

    def list_projects(self) -> list[ProjectId]:
        return sorted(self._index.keys())

    def state_path_for(self, project_id: ProjectId) -> Path:
        return self._state_path(project_id)
