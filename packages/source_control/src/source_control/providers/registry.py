"""Provider registry — Git default, remote providers as extension points."""

from __future__ import annotations

from source_control.errors import ProviderNotAvailableError
from source_control.providers.git import GitProvider


class ProviderRegistry:
    """Registry of source control providers."""

    def __init__(self) -> None:
        self._providers: dict[str, object] = {
            "git": GitProvider(),
            "github": _GitHubProvider(),
            "gitlab": _GitLabProvider(),
            "azure_devops": _AzureDevOpsProvider(),
            "bitbucket": _BitbucketProvider(),
        }
        self._default = "git"

    def get(self, provider_id: str | None = None):
        pid = provider_id or self._default
        provider = self._providers.get(pid)
        if provider is None:
            raise ProviderNotAvailableError(f"Unknown provider: {pid}")
        if pid == "git" and not provider.is_available():
            raise ProviderNotAvailableError("Git is not available on this system")
        return provider

    def list_providers(self) -> list[dict]:
        return [
            {
                "id": pid,
                "available": p.is_available() if hasattr(p, "is_available") else False,
                "implemented": pid == "git",
            }
            for pid, p in self._providers.items()
        ]


class _RemoteProviderStub:
    """Placeholder for future remote provider integration."""

    provider_id: str = "remote"

    def is_available(self) -> bool:
        return False


class _GitHubProvider(_RemoteProviderStub):
    provider_id = "github"


class _GitLabProvider(_RemoteProviderStub):
    provider_id = "gitlab"


class _AzureDevOpsProvider(_RemoteProviderStub):
    provider_id = "azure_devops"


class _BitbucketProvider(_RemoteProviderStub):
    provider_id = "bitbucket"
