#!/usr/bin/env python3
# packages/cherenkov/dev_crew/github_issue_source.py
"""
GitHub Issue Source — fetches open issues and maps them to swarm tasks.

Priority order: critical > high > medium > low, then by milestone due date.
Issue routing:
  - area:scanner + ai:autonomous  → CWE scanner pipeline (Ollama)
  - has .agents/tasks/issue-NNN.md → AutonomousSprint (code sprint)
  - otherwise                      → skip (manual only)
"""

from __future__ import annotations

import json
import logging
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Literal

logger = logging.getLogger("cherenkov.swarm.github")

TASKS_DIR = Path(".agents/tasks")
ISSUE_QUEUE = Path("manifests/issue_queue.yaml")

# Priority weight: lower = higher priority
_PRIORITY_WEIGHT: dict[str, int] = {
    "priority:critical": 0,
    "priority:high": 1,
    "priority:medium": 2,
    "priority:low": 3,
}

TaskKind = Literal["scanner", "sprint", "skip"]


@dataclass
class IssueTask:
    number: int
    title: str
    labels: list[str]
    milestone_title: str
    milestone_due: str  # ISO date string or ""
    task_file: Path | None  # .agents/tasks/issue-NNN.md if exists
    kind: TaskKind
    priority_weight: int
    status: str = "pending"  # pending | in_progress | done | failed

    # Derived fields for executor
    branch: str = ""
    description: str = ""  # short description extracted from title

    def __post_init__(self) -> None:
        if not self.branch:
            # Extract branch from task file or synthesise one
            self.branch = self._parse_branch() or f"agent/issue-{self.number}"
        if not self.description:
            # Strip [ANN] prefix from title
            import re
            self.description = re.sub(r"^\[A\d+\]\s*", "", self.title)

    def _parse_branch(self) -> str:
        if self.task_file and self.task_file.exists():
            for line in self.task_file.read_text().splitlines():
                if line.startswith("**Branch:**"):
                    return line.split("`")[1] if "`" in line else ""
        return ""


class GitHubIssueSource:
    """Fetches open GitHub issues and classifies them as swarm tasks."""

    def __init__(self, repo: str = "") -> None:
        # repo = "owner/name" or "" to auto-detect from git remote
        self.repo = repo

    def fetch_pending(self, limit: int = 30) -> list[IssueTask]:
        """
        Returns open issues that the swarm can process, sorted by priority.
        Excludes issues already tracked in issue_queue.yaml as done/in_progress.
        """
        raw_issues = self._gh_list_issues(limit)
        in_flight = self._load_in_flight()

        tasks: list[IssueTask] = []
        for issue in raw_issues:
            num = issue["number"]
            if num in in_flight:
                continue
            task = self._classify(issue)
            if task.kind != "skip":
                tasks.append(task)

        # Sort: priority weight first, then milestone due date ascending
        tasks.sort(key=lambda t: (t.priority_weight, t.milestone_due or "9999"))
        return tasks

    # ── gh CLI wrappers ──────────────────────────────────────────────────────

    def _gh_list_issues(self, limit: int) -> list[dict]:
        cmd = [
            "gh", "issue", "list",
            "--limit", str(limit),
            "--state", "open",
            "--json", "number,title,labels,milestone",
        ]
        if self.repo:
            cmd += ["--repo", self.repo]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                logger.warning("gh issue list failed: %s", result.stderr[:200])
                return []
            return json.loads(result.stdout or "[]")
        except Exception as e:
            logger.warning("GitHub fetch error: %s", e)
            return []

    @staticmethod
    def gh_comment(issue_number: int, body: str, repo: str = "") -> None:
        cmd = ["gh", "issue", "comment", str(issue_number), "--body", body]
        if repo:
            cmd += ["--repo", repo]
        subprocess.run(cmd, capture_output=True, timeout=30)

    @staticmethod
    def gh_add_label(issue_number: int, label: str, repo: str = "") -> None:
        cmd = ["gh", "issue", "edit", str(issue_number), "--add-label", label]
        if repo:
            cmd += ["--repo", repo]
        subprocess.run(cmd, capture_output=True, timeout=30)

    @staticmethod
    def gh_remove_label(issue_number: int, label: str, repo: str = "") -> None:
        cmd = ["gh", "issue", "edit", str(issue_number), "--remove-label", label]
        if repo:
            cmd += ["--repo", repo]
        subprocess.run(cmd, capture_output=True, timeout=30)

    @staticmethod
    def gh_create_pr(branch: str, title: str, body: str, repo: str = "") -> str:
        """Returns PR URL or empty string on failure."""
        cmd = [
            "gh", "pr", "create",
            "--head", branch,
            "--title", title,
            "--body", body,
        ]
        if repo:
            cmd += ["--repo", repo]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                return result.stdout.strip()
            logger.warning("gh pr create failed: %s", result.stderr[:200])
            return ""
        except Exception as e:
            logger.warning("PR creation error: %s", e)
            return ""

    # ── Classification ───────────────────────────────────────────────────────

    def _classify(self, issue: dict) -> IssueTask:
        num = issue["number"]
        title = issue.get("title", "")
        label_names = [lb["name"] for lb in issue.get("labels", [])]
        ms = issue.get("milestone") or {}
        milestone_title = ms.get("title", "")
        due_on = ms.get("dueOn", "") or ""
        # Normalise ISO: "2026-09-10T00:00:00Z" → "2026-09-10"
        milestone_due = due_on[:10] if due_on else ""

        priority_weight = min(
            (_PRIORITY_WEIGHT.get(lb, 4) for lb in label_names),
            default=4,
        )

        task_file = TASKS_DIR / f"issue-{num}.md"
        if not task_file.exists():
            task_file = None

        # Routing logic
        is_scanner = "area:scanner" in label_names and "ai:autonomous" in label_names
        has_sprint = task_file is not None

        if is_scanner:
            kind: TaskKind = "scanner"
        elif has_sprint:
            kind = "sprint"
        else:
            kind = "skip"

        return IssueTask(
            number=num,
            title=title,
            labels=label_names,
            milestone_title=milestone_title,
            milestone_due=milestone_due,
            task_file=task_file,
            kind=kind,
            priority_weight=priority_weight,
        )

    # ── State tracking ───────────────────────────────────────────────────────

    def _load_in_flight(self) -> set[int]:
        """Return issue numbers already tracked as in_progress or done."""
        if not ISSUE_QUEUE.exists():
            return set()
        try:
            import yaml
            data = yaml.safe_load(ISSUE_QUEUE.read_text()) or {}
            return {
                item["number"]
                for item in data.get("issues", [])
                if item.get("status") in ("in_progress", "done")
            }
        except Exception:
            return set()

    @staticmethod
    def upsert_issue_state(
        number: int,
        status: str,
        title: str = "",
        kind: str = "",
        branch: str = "",
        pr_url: str = "",
        fail_reason: str = "",
    ) -> None:
        import yaml

        ISSUE_QUEUE.parent.mkdir(parents=True, exist_ok=True)
        data: dict = {}
        if ISSUE_QUEUE.exists():
            data = yaml.safe_load(ISSUE_QUEUE.read_text()) or {}
        issues: list[dict] = data.get("issues", [])

        for item in issues:
            if item["number"] == number:
                item["status"] = status
                if pr_url:
                    item["pr_url"] = pr_url
                if fail_reason:
                    item["fail_reason"] = fail_reason[:300]
                item["updated_at"] = datetime.utcnow().isoformat()
                break
        else:
            issues.append({
                "number": number,
                "title": title,
                "kind": kind,
                "branch": branch,
                "status": status,
                "pr_url": pr_url,
                "fail_reason": fail_reason[:300] if fail_reason else "",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            })
        data["issues"] = issues
        ISSUE_QUEUE.write_text(yaml.dump(data, default_flow_style=False, allow_unicode=True))
