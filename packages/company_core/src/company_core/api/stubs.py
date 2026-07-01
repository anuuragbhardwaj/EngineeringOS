"""Placeholder API implementations for future phases."""

from __future__ import annotations

from company_core.models.common import EmployeeInfo
from company_core.models.errors import NotImplementedFeatureError


class EmployeeAPI:
    def list(self) -> list[EmployeeInfo]:
        raise NotImplementedFeatureError("employees list is not yet implemented")

    def get(self, employee_id: str) -> object:
        raise NotImplementedFeatureError("employee get is not yet implemented")

    def for_phase(self, phase_id: str) -> list[object]:
        raise NotImplementedFeatureError("employees for_phase is not yet implemented")

    def resolve_path(self, employee_id: str) -> object:
        raise NotImplementedFeatureError("employee resolve_path is not yet implemented")


class IntegrationAPI:
    def install(self, editor: str) -> object:
        raise NotImplementedFeatureError("integration install is not yet implemented")

    def uninstall(self, editor: str) -> None:
        raise NotImplementedFeatureError("integration uninstall is not yet implemented")

    def list_editors(self) -> list[object]:
        raise NotImplementedFeatureError("integration list_editors is not yet implemented")

    def sync(self, editor: str) -> object:
        raise NotImplementedFeatureError("integration sync is not yet implemented")

    def doctor(self, editor: str) -> object:
        raise NotImplementedFeatureError("integration doctor is not yet implemented")
