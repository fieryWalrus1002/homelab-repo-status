import logging
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from homelab_repo_status.config import config

logger = logging.getLogger(__name__)


@dataclass
class GitState:
    is_git_repo: bool
    has_uncommitted_changes: bool
    uncommitted_files: list[str]
    is_up_to_date_with_remote: bool
    has_unpushed_commits: bool
    unpushed_commit_count: int


def _run(args: list[str], cwd: Path) -> tuple[int, str]:
    cmd = " ".join(args)
    t0 = time.perf_counter()
    try:
        result = subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=config["git"]["command_timeout"],
        )
        elapsed = time.perf_counter() - t0
        logger.debug(
            "git cmd=%-50s repo=%-30s rc=%d elapsed=%.3fs",
            cmd,
            cwd.name,
            result.returncode,
            elapsed,
        )
        return result.returncode, result.stdout.rstrip()
    except subprocess.TimeoutExpired:
        elapsed = time.perf_counter() - t0
        logger.warning("git cmd=%-50s repo=%-30s TIMEOUT elapsed=%.3fs", cmd, cwd.name, elapsed)
        return 1, ""


def get_git_state(repo_path: Path) -> GitState:
    logger.info("scanning repo=%s", repo_path.name)
    t0 = time.perf_counter()

    rc, _ = _run(["git", "rev-parse", "--is-inside-work-tree"], repo_path)
    if rc != 0:
        logger.info("repo=%s is_git_repo=false", repo_path.name)
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

    _, _ = _run(["git", "fetch", "--quiet"], repo_path)

    rc, ahead_behind = _run(
        ["git", "rev-list", "--left-right", "--count", "@{u}...HEAD"], repo_path
    )
    if rc != 0:
        is_up_to_date = True
        unpushed_count = 0
    else:
        parts = ahead_behind.split()
        behind = int(parts[0]) if len(parts) > 0 else 0
        ahead = int(parts[1]) if len(parts) > 1 else 0
        is_up_to_date = ahead == 0 and behind == 0
        unpushed_count = ahead

    elapsed = time.perf_counter() - t0
    logger.info(
        "repo=%-30s elapsed=%.3fs uncommitted=%d unpushed=%d in_sync=%s",
        repo_path.name,
        elapsed,
        len(uncommitted_files),
        unpushed_count,
        is_up_to_date,
    )

    return GitState(
        is_git_repo=True,
        has_uncommitted_changes=len(uncommitted_files) > 0,
        uncommitted_files=uncommitted_files,
        is_up_to_date_with_remote=is_up_to_date,
        has_unpushed_commits=unpushed_count > 0,
        unpushed_commit_count=unpushed_count,
    )
