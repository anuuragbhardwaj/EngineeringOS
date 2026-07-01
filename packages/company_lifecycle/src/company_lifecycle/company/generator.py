"""Generate user-owned company assets."""

from __future__ import annotations

import subprocess
from pathlib import Path

from company_lifecycle.filesystem.boundaries import assert_no_framework_assets
from company_lifecycle.installation.detector import discover_installed_framework, framework_version
from company_lifecycle.manifest.generator import build_company_manifest, write_company_manifest
from company_lifecycle.types import CompanyCreateRequest


def generate_company(request: CompanyCreateRequest) -> Path:
    """Create a generated company — user-owned assets only."""
    assert_no_framework_assets([])

    framework_root = request.framework_install_path or discover_installed_framework()
    if framework_root is None:
        from company_lifecycle.errors import FrameworkNotInstalledError

        raise FrameworkNotInstalledError(
            "EngineeringOS framework not found. Install with: pip install -e ."
        )

    request.framework_install_path = framework_root
    target = request.target.resolve()
    if (target / "company.yaml").exists():
        raise FileExistsError(f"Company already exists at {target}")

    manifest = build_company_manifest(request, framework_version())
    manifest_path = write_company_manifest(target, manifest)

    (target / "workspaces").mkdir(parents=True, exist_ok=True)
    (target / "docs").mkdir(parents=True, exist_ok=True)
    readme = target / "README.md"
    if not readme.exists():
        readme.write_text(
            _company_readme(request, framework_root),
            encoding="utf-8",
        )

    gitignore = target / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text(
            "# Generated company\nworkspaces/*/.company/cache/\n.env\n",
            encoding="utf-8",
        )

    if request.init_github:
        github_dir = target / ".github"
        github_dir.mkdir(parents=True, exist_ok=True)
        workflows = github_dir / "workflows"
        workflows.mkdir(exist_ok=True)
        ci = workflows / "engineeringos.yml"
        if not ci.exists():
            ci.write_text(
                "name: EngineeringOS\n"
                "on: [push, pull_request]\n"
                "jobs:\n"
                "  validate:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - uses: actions/checkout@v4\n"
                "      - run: echo Run engineeringos validate in your environment\n",
                encoding="utf-8",
            )

    if request.documentation_enabled:
        docs_readme = target / "docs" / "README.md"
        if not docs_readme.exists():
            docs_readme.write_text(
                f"# {request.name}\n\nCompany documentation.\n",
                encoding="utf-8",
            )

    if request.init_git:
        _init_git(target)

    return manifest_path


def _company_readme(request: CompanyCreateRequest, framework_root: Path) -> str:
    return (
        f"# {request.name}\n\n"
        "Generated company instance for EngineeringOS.\n\n"
        "## Framework reference\n\n"
        f"This company references the installed EngineeringOS framework at:\n\n"
        f"`{framework_root}`\n\n"
        "Framework source code is **not** copied into this company.\n\n"
        "## Commands\n\n"
        "```bash\n"
        "engineeringos open\n"
        "engineeringos workspace list\n"
        "engineeringos project create --yes --name \"My App\"\n"
        "engineeringos doctor\n"
        "```\n"
    )


def _init_git(target: Path) -> None:
    try:
        subprocess.run(
            ["git", "init"],
            cwd=target,
            check=False,
            capture_output=True,
        )
    except OSError:
        pass
