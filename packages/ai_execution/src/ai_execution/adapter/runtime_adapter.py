"""Runtime IAgentAdapter — translates between kernel types and execution platform."""

from __future__ import annotations

from pathlib import Path

from ai_execution.platform import ExecutionPlatform
from ai_execution.types import IAgentAdapter


class RuntimeAgentAdapter:
    """IAgentAdapter implementation — sole boundary from Runtime to AI Execution Platform."""

    def __init__(self, platform: ExecutionPlatform) -> None:
        self._platform = platform

    def invoke(self, descriptor, context):
        from runtime_engine.types import AdapterResult, AdapterStatus

        project_root = Path(context.artifact_root)
        self._platform.set_project_storage(project_root)

        response = self._platform.execute(descriptor, context)
        result = response.result

        status_map = {
            "completed": AdapterStatus.COMPLETED,
            "pending": AdapterStatus.PENDING,
            "failed": AdapterStatus.FAILED,
            "delegated": AdapterStatus.DELEGATED,
        }
        status = status_map.get(result.status.value, AdapterStatus.COMPLETED)

        return AdapterResult(
            status=status,
            agent_id=descriptor.agent_id,
            phase_id=descriptor.phase_id,
            message=result.message,
            job_id=result.job_id,
            artifacts_touched=result.artifacts_touched,
            metadata={
                **result.metadata,
                "provider_id": response.provider_id,
                "request_id": response.request_id,
                "duration_ms": response.duration_ms,
            },
        )

    def cancel(self, job_id: str) -> bool:
        return False

    def health(self):
        from runtime_engine.types import AdapterHealth

        diag = self._platform.diagnostics()
        cursor = diag.get("providers", {}).get("cursor", {})
        available = cursor.get("available", False)
        return AdapterHealth(
            available=available or diag.get("providers", {}).get("scaffold", {}).get(
                "available", True
            ),
            message="AI Execution Platform ready",
        )


def create_runtime_adapter(
    framework_root: Path | None = None,
    providers_config: Path | None = None,
) -> IAgentAdapter:
    from ai_execution.factory import create_platform

    platform = create_platform(framework_root, providers_config)
    return RuntimeAgentAdapter(platform)
