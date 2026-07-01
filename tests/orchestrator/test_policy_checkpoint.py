"""Policy and checkpoint tests."""

from pathlib import Path

from orchestrator.checkpoint.manager import CheckpointManager
from orchestrator.policy.engine import PolicyEngine

REPO_ROOT = Path(__file__).resolve().parents[2]
POLICIES = REPO_ROOT / "packages" / "orchestrator" / "policies.yaml"


def test_policy_resolution() -> None:
    engine = PolicyEngine()
    engine.load(POLICIES)
    policy = engine.resolve("planning", "G3")
    assert policy.name == "sequential"
    assert policy.mcp_evidence_required is True


def test_retry_policy() -> None:
    engine = PolicyEngine()
    engine.load(POLICIES)
    policy = engine.resolve("idea")
    assert engine.should_retry(policy, 0, True) is True
    assert engine.should_retry(policy, 2, True) is False


def test_checkpoint_lifecycle() -> None:
    mgr = CheckpointManager()
    cp = mgr.create("proj", "idea", "engineering-manager")
    mgr.pause(cp.checkpoint_id)
    assert mgr.get_active("proj").status == "paused"
    mgr.complete(cp.checkpoint_id)
