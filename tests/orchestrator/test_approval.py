"""Approval hook tests."""

import pytest

from orchestrator.approval.hooks import ApprovalHooks
from orchestrator.errors import ApprovalRequiredError


def test_approval_pause_and_resume() -> None:
    hooks = ApprovalHooks()
    key = hooks.approval_key("proj", "G0")
    hooks.request(key)
    with pytest.raises(ApprovalRequiredError):
        hooks.require(key)
    hooks.approve(key)
    hooks.require(key)
