"""SDLC completion and source control automation."""

from __future__ import annotations

from pathlib import Path

from autonomous_company.approvals.engine import ApprovalEngine
from autonomous_company.policies.store import AutonomousStore


class SdlcCompletion:
    """Complete SDLC cycle with automated source control after approval."""

    def __init__(self) -> None:
        self._store = AutonomousStore()
        self._approvals = ApprovalEngine(self._store)

    def run(
        self,
        instance_root: Path,
        *,
        project_id: str | None = None,
        run_tests: bool = True,
        auto_push: bool | None = None,
    ) -> dict:
        """Run testing → review gates → commit flow."""
        from workspace_execution.resolver.resolver import ContextResolver

        ctx = ContextResolver().resolve(instance_root)
        pid = project_id or ctx.session.project_id or "company"
        policy = self._store.load_policy(instance_root)
        push_allowed = auto_push if auto_push is not None else policy.auto_push

        report: dict = {"project_id": pid, "steps": []}

        # 1. Validate
        if run_tests:
            test_result = self._run_tests(instance_root)
            report["steps"].append({"step": "testing", "result": test_result})
            if not test_result.get("passed", True):
                report["status"] = "blocked"
                report["reason"] = "Tests failed"
                return report

        # 2. Repository validation
        sc_result = self._validate_repo(instance_root)
        report["steps"].append({"step": "repo_validate", "result": sc_result})
        if not sc_result.get("valid", False):
            report["status"] = "blocked"
            report["reason"] = "Repository validation failed"
            return report

        # 3. Request and check commit approval
        if self._approvals.requires_approval(instance_root, "commit"):
            if not self._approvals.is_approved(instance_root, pid, "commit"):
                self._approvals.request(instance_root, pid, "commit", reason="SDLC completion")
                report["status"] = "blocked"
                report["reason"] = "Commit approval required — run: engineeringos approvals approve commit"
                return report

        # 4. Generate commit, stage, commit
        commit_result = self._auto_commit(instance_root, pid)
        report["steps"].append({"step": "commit", "result": commit_result})
        if not commit_result.get("sha"):
            report["status"] = "blocked"
            report["reason"] = commit_result.get("error", "Commit failed")
            return report

        # 5. Release notes
        release_result = self._prepare_release(instance_root)
        report["steps"].append({"step": "release_notes", "result": release_result})

        # 6. Push if policy allows
        if push_allowed:
            if self._approvals.is_approved(instance_root, pid, "push") or self._approvals.approve(instance_root, pid, "push"):
                push_result = self._push(instance_root, pid)
                report["steps"].append({"step": "push", "result": push_result})

        report["status"] = "completed"
        report["commit_sha"] = commit_result.get("sha")
        self._record_commit_history(instance_root, pid, commit_result.get("sha", ""))
        return report

    def _run_tests(self, instance_root: Path) -> dict:
        import subprocess

        framework = instance_root
        for parent in [instance_root, *instance_root.parents]:
            if (parent / "pyproject.toml").is_file() and (parent / "tests").is_dir():
                framework = parent
                break
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "tests", "-q", "--tb=no"],
                cwd=framework,
                capture_output=True,
                text=True,
                timeout=120,
            )
            return {"passed": result.returncode == 0, "output": result.stdout[-500:]}
        except Exception as exc:
            return {"passed": False, "error": str(exc)}

    def _validate_repo(self, instance_root: Path) -> dict:
        try:
            from source_control.factory import create_source_control_platform

            sc = create_source_control_platform()
            return sc.validate(instance_root)
        except Exception as exc:
            return {"valid": False, "error": str(exc)}

    def _auto_commit(self, instance_root: Path, project_id: str) -> dict:
        try:
            from source_control.factory import create_source_control_platform

            sc = create_source_control_platform()
            sc.approve(instance_root, "commit", project_id)
            msg = sc.generate_commit(instance_root, phase_id="release")
            sc.stage(instance_root)
            result = sc.commit(instance_root, message=msg.full_message, require_approval=True)
            return result.to_dict()
        except Exception as exc:
            return {"error": str(exc)}

    def _prepare_release(self, instance_root: Path) -> dict:
        try:
            from source_control.factory import create_source_control_platform

            sc = create_source_control_platform()
            plan = sc.release(instance_root)
            return plan.to_dict()
        except Exception as exc:
            return {"error": str(exc)}

    def _push(self, instance_root: Path, project_id: str) -> dict:
        try:
            from source_control.factory import create_source_control_platform

            sc = create_source_control_platform()
            return sc.push(instance_root, require_approval=True)
        except Exception as exc:
            return {"error": str(exc)}

    def _record_commit_history(self, instance_root: Path, project_id: str, sha: str) -> None:
        try:
            from workspace_execution.history.recorder import record_event

            record_event(instance_root, event_type="sdlc_commit", project_id=project_id, detail=sha)
        except Exception:
            pass
