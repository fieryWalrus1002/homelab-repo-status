import subprocess
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class GitState:
    is_git_repo: bool
    has_uncommitted_changes: bool
    uncommitted_files: list[str]
    is_up_to_date_with_remote: bool
    has_unpushed_commits: bool
    unpushed_commit_count: int


def _run(args: list[str], cwd: Path) -> tuple[int, str]:
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    return result.returncode, result.stdout.strip()


def get_git_state(repo_path: Path) -> GitState:
    rc, _ = _run(["git", "rev-parse", "--is-inside-work-tree"], repo_path)
    if rc != 0:
        return GitState(
            is_git_repo=False,
            has_uncommitted_changes=False,
            uncommitted_files=[],
            is_up_to_date_with_remote=True,
            has_unpushed_commits=False,
            unpushed_commit_count=0,
        )

    _, status_out = _run(["git", "status", "--porcelain"], repo_path)
    uncommitted_files = [line[3:] for line in status_out.splitlines() if line.strip()]

    subprocess.run(["git", "fetch", "--quiet"], cwd=repo_path, capture_output=True)

    rc, ahead_behind = _run(
        ["git", "rev-list", "--left-right", "--count", "@{u}...HEAD"], repo_path
    )
    if rc != 0:
        # No upstream tracking branch configured
        is_up_to_date = True
        unpushed_count = 0
    else:
        parts = ahead_behind.split()
        behind = int(parts[0]) if len(parts) > 0 else 0
        ahead = int(parts[1]) if len(parts) > 1 else 0
        is_up_to_date = ahead == 0 and behind == 0
        unpushed_count = ahead

    return GitState(
        is_git_repo=True,
        has_uncommitted_changes=len(uncommitted_files) > 0,
        uncommitted_files=uncommitted_files,
        is_up_to_date_with_remote=is_up_to_date,
        has_unpushed_commits=unpushed_count > 0,
        unpushed_commit_count=unpushed_count,
    )
