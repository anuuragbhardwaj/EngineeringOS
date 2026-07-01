"""Knowledge platform tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from knowledge.errors import KnowledgePromotionError, KnowledgeValidationError
from knowledge.factory import create_knowledge_platform
from knowledge.types import KnowledgeQuery, KnowledgeScope, KnowledgeStatus, RetrievalContext


@pytest.fixture
def company_root(tmp_path: Path) -> Path:
    (tmp_path / "company.yaml").write_text(
        "company:\n  instance_id: test-co\n  instance_version: '1.0.0'\n"
        "  schema_version: '1.0.0'\n  framework:\n    version: '2.0.0'\n"
        "  configuration:\n    workspaces_root: workspaces/\n    default_workspace: default\n",
        encoding="utf-8",
    )
    return tmp_path


def test_capture_and_persist(company_root: Path) -> None:
    platform = create_knowledge_platform()
    knowledge = platform.capture(
        company_root,
        title="Use pytest for tests",
        content="All packages must have automated tests.",
        origin="qa-engineer",
        owner="qa-engineer",
        reason="Testing convention",
        project_id="my-app",
        confidence=0.8,
        auto_activate=True,
    )
    assert knowledge.id
    loaded = platform.get(company_root, knowledge.id)
    assert loaded.title == "Use pytest for tests"
    assert loaded.status == KnowledgeStatus.ACTIVE.value


def test_framework_knowledge_loaded(company_root: Path) -> None:
    platform = create_knowledge_platform()
    framework_items = platform.store.load_framework_knowledge()
    assert len(framework_items) >= 2
    assert all(item.scope == KnowledgeScope.FRAMEWORK.value for item in framework_items)


def test_validation_rejects_empty_title(company_root: Path) -> None:
    platform = create_knowledge_platform()
    knowledge = platform.capture(
        company_root,
        title="",
        content="content",
        origin="test",
        owner="test",
        reason="test",
    )
    result = platform.validate(company_root, knowledge.id)
    assert not result.valid


def test_promotion_requires_confidence(company_root: Path) -> None:
    platform = create_knowledge_platform()
    knowledge = platform.capture(
        company_root,
        title="Low confidence note",
        content="Maybe useful",
        origin="conversation",
        owner="dev",
        reason="captured from chat",
        scope=KnowledgeScope.CONVERSATION.value,
        confidence=0.3,
        conversation_id="conv-1",
    )
    with pytest.raises(KnowledgePromotionError):
        platform.promote(company_root, knowledge.id, reviewer_approved=True)


def test_promotion_success(company_root: Path) -> None:
    platform = create_knowledge_platform()
    knowledge = platform.capture(
        company_root,
        title="API uses REST",
        content="All endpoints are RESTful JSON APIs.",
        origin="architecture",
        owner="engineering-manager",
        reason="Architecture decision",
        knowledge_type="architecture_decision",
        scope=KnowledgeScope.PROJECT.value,
        project_id="api-service",
        confidence=0.85,
        auto_activate=True,
    )
    promoted = platform.promote(
        company_root,
        knowledge.id,
        target_scope=KnowledgeScope.WORKSPACE.value,
        reviewer_approved=True,
    )
    assert promoted.scope == KnowledgeScope.WORKSPACE.value
    assert promoted.version == 2
    history = platform.history(company_root, knowledge.id)
    assert any(not h.rejected for h in history)


def test_knowledge_graph_relations(company_root: Path) -> None:
    platform = create_knowledge_platform()
    a = platform.capture(
        company_root,
        title="Decision A",
        content="First decision",
        origin="em",
        owner="em",
        reason="test",
        confidence=0.8,
        auto_activate=True,
    )
    b = platform.capture(
        company_root,
        title="Decision B",
        content="Depends on A",
        origin="em",
        owner="em",
        reason="test",
        confidence=0.8,
        auto_activate=True,
    )
    platform.add_relation(company_root, b.id, a.id, "depends_on")
    neighbors = platform.graph.neighbors(company_root, b.id)
    assert len(neighbors) == 1
    assert neighbors[0]["relation_type"] == "depends_on"


def test_context_aware_retrieval(company_root: Path) -> None:
    platform = create_knowledge_platform()
    platform.capture(
        company_root,
        title="Project-specific rule",
        content="Use black formatting.",
        origin="dev",
        owner="dev",
        reason="convention",
        project_id="app-a",
        confidence=0.9,
        auto_activate=True,
    )
    platform.capture(
        company_root,
        title="Other project rule",
        content="Use tabs.",
        origin="dev",
        owner="dev",
        reason="convention",
        project_id="app-b",
        confidence=0.9,
        auto_activate=True,
    )
    results = platform.retrieve(
        company_root,
        RetrievalContext(project_id="app-a", max_items=5),
    )
    assert results
    assert any(r.knowledge.project_id == "app-a" for r in results)


def test_search_and_stats(company_root: Path) -> None:
    platform = create_knowledge_platform()
    platform.capture(
        company_root,
        title="Bug pattern: null pointer",
        content="Always check null before dereference.",
        origin="qa",
        owner="qa",
        reason="recurring bug",
        knowledge_type="bug_pattern",
        confidence=0.75,
        auto_activate=True,
    )
    results = platform.search(company_root, KnowledgeQuery(text="null pointer"))
    assert len(results) >= 1
    stats = platform.stats(company_root)
    assert stats.total >= 1
    assert stats.by_type.get("bug_pattern", 0) >= 1


def test_export_import_roundtrip(company_root: Path) -> None:
    platform = create_knowledge_platform()
    platform.capture(
        company_root,
        title="Exportable fact",
        content="Can be exported.",
        origin="test",
        owner="test",
        reason="export test",
        confidence=0.8,
        auto_activate=True,
    )
    bundle = platform.export_bundle(company_root)
    assert bundle["knowledge"]
    # Import into fresh dir
    other = company_root / "other"
    other.mkdir()
    (other / "company.yaml").write_text(
        (company_root / "company.yaml").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    count = platform.import_bundle(other, bundle)
    assert count >= 1


def test_event_handler_captures_phase_completed(company_root: Path) -> None:
    platform = create_knowledge_platform()
    platform.handle_event(
        company_root,
        "PhaseCompleted",
        {"project_id": "p1", "phase_id": "implementation"},
    )
    results = platform.search(company_root, KnowledgeQuery(project_id="p1"))
    assert any("Phase completed" in r.title for r in results)


def test_aging_archives_conversation_knowledge(company_root: Path) -> None:
    from datetime import datetime, timedelta

    from knowledge.aging.aging import KnowledgeAging
    from knowledge.types import KnowledgeObject, utc_now

    platform = create_knowledge_platform()
    old_time = (datetime.utcnow() - timedelta(days=60)).isoformat()
    obj = KnowledgeObject(
        id=platform.store.new_id(),
        knowledge_type="fact",
        scope=KnowledgeScope.CONVERSATION.value,
        title="Old chat note",
        content="temporary",
        origin="chat",
        owner="dev",
        reason="conversation",
        confidence=0.5,
        status=KnowledgeStatus.ACTIVE.value,
        created_at=old_time,
        updated_at=old_time,
        conversation_id="c-old",
    )
    platform.store.save(company_root, obj)
    # save() stamps updated_at — restore aged timestamps for policy test
    import yaml
    from knowledge.store.paths import knowledge_file

    path = knowledge_file(company_root, KnowledgeScope.CONVERSATION.value, obj.id)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["created_at"] = old_time
    data["updated_at"] = old_time
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    aging = KnowledgeAging(platform.store)
    affected = aging.apply_aging_policies(company_root)
    assert obj.id in affected
    archived = platform.get(company_root, obj.id)
    assert archived.status == KnowledgeStatus.ARCHIVED.value
