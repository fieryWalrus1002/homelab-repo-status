import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from homelab_repo_status.git_state import get_git_state
from homelab_repo_status.output import write_records

logger = logging.getLogger(__name__)


def _repos_dir() -> Path:
    return Path(os.environ.get("REPOS_DIR", str(Path.home() / "repos")))


def collect(repos_dir: Path | None = None) -> list[dict]:
    base = repos_dir or _repos_dir()
    timestamp = datetime.now(timezone.utc).isoformat()
    records = []

    entries = [e for e in sorted(base.iterdir()) if e.is_dir()]
    logger.info("starting scan repos_dir=%s count=%d", base, len(entries))
    t0 = time.perf_counter()

    for entry in entries:
        state = get_git_state(entry)
        records.append(
            {
                "repo_name": entry.name,
                "repo_path": str(entry),
                "is_git_repo": state.is_git_repo,
                "has_uncommitted_changes": state.has_uncommitted_changes,
                "uncommitted_files": state.uncommitted_files,
                "is_up_to_date_with_remote": state.is_up_to_date_with_remote,
                "has_unpushed_commits": state.has_unpushed_commits,
                "unpushed_commit_count": state.unpushed_commit_count,
                "scan_timestamp": timestamp,
            }
        )

    elapsed = time.perf_counter() - t0
    logger.info("scan complete repos=%d elapsed=%.3fs", len(records), elapsed)
    return records


def main() -> None:
    records = collect()
    write_records(records)
    print(f"Scanned {len(records)} repositories.")


if __name__ == "__main__":
    main()
