"""Filesystem ownership boundaries — framework vs company vs workspace vs project."""

from __future__ import annotations

# Framework-owned — never copy into generated companies
FRAMEWORK_OWNED = frozenset(
    {
        "packages",
        "runtime",
        "mcp",
        "handbook",
        "workflow.yaml",
        "workflow-v1.md",
        "pyproject.toml",
        ".cursor",
        "mcp_platform",
    }
)

# Company-owned — generated at company init
COMPANY_OWNED = frozenset(
    {
        "company.yaml",
        "README.md",
        "workspaces",
        "docs",
        ".github",
        ".gitignore",
        ".company",
    }
)

# Workspace-owned
WORKSPACE_OWNED = frozenset(
    {
        ".company",
        "projects",
        "extensions",
        "user",
    }
)

# Project-owned
PROJECT_OWNED = frozenset(
    {
        ".company-project.yaml",
        "README.md",
        "src",
        "tests",
        "docs",
    }
)

# Tool-generated — created by EngineeringOS tools, not user source
TOOL_GENERATED = frozenset(
    {
        ".runtime",
        ".company",
    }
)


def assert_no_framework_assets(paths: list[str]) -> None:
    """Raise if any path would copy framework-owned content into a company."""
    from company_lifecycle.errors import OwnershipViolationError

    for path in paths:
        name = path.replace("\\", "/").split("/")[0]
        if name in FRAMEWORK_OWNED:
            raise OwnershipViolationError(
                f"Cannot copy framework-owned asset into company: {path}"
            )
