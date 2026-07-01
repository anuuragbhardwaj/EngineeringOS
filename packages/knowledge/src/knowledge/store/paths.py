"""Knowledge filesystem paths inside generated companies."""

from __future__ import annotations

from pathlib import Path

KNOWLEDGE_ROOT = Path(".company") / "knowledge"

SCOPE_DIRS = (
    "framework",
    "company",
    "workspace",
    "project",
    "employee",
    "conversation",
    "relationships",
    "indexes",
    "promotions",
    "versions",
)


def knowledge_paths(instance_root: Path) -> dict[str, Path]:
    base = instance_root / KNOWLEDGE_ROOT
    return {name: base / name for name in SCOPE_DIRS}


def ensure_knowledge_dirs(instance_root: Path) -> None:
    for path in knowledge_paths(instance_root).values():
        path.mkdir(parents=True, exist_ok=True)


def scope_dir(instance_root: Path, scope: str) -> Path:
    paths = knowledge_paths(instance_root)
    if scope not in paths:
        raise ValueError(f"Unknown knowledge scope: {scope}")
    directory = paths[scope]
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def knowledge_file(instance_root: Path, scope: str, knowledge_id: str) -> Path:
    return scope_dir(instance_root, scope) / f"{knowledge_id}.yaml"


def relations_file(instance_root: Path) -> Path:
    return knowledge_paths(instance_root)["relationships"] / "graph.yaml"


def promotions_file(instance_root: Path) -> Path:
    return knowledge_paths(instance_root)["promotions"] / "history.yaml"


def framework_knowledge_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "framework"
