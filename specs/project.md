# Project Specification: homelab-repo-status

## Summary

Build a minimal Python uv-based utility that scans repositories under `~/repos`, captures their Git status, writes results to JSONL, and provides local visibility through a FastAPI app. The system is intended for local homelab usage and local deployment with Docker Compose.

## Goals

1. Discover repositories under `~/repos`.
2. For each repository, capture:
   - uncommitted file changes
   - local vs remote sync status
   - unpushed local commits
   - local files not yet committed
3. Store scan output in JSONL format.
4. Surface scan data in a local FastAPI web app.
5. Start services through Docker Compose.

## Non-Goals

- Full enterprise Git hosting integration.
- Multi-user authentication/authorization.
- Distributed or cloud deployment concerns.
- Advanced analytics beyond repository status visibility.

## Functional Requirements

- The scanner must iterate each immediate subfolder in `~/repos`.
- Non-Git directories should be handled gracefully.
- The collector should inspect Git state from the local checkout and remote tracking metadata.
- Output must be line-delimited JSON (`.jsonl`) with one record per repository per scan.
- The FastAPI app should read from JSONL and provide local endpoints for status inspection.

## Suggested JSONL Record Shape

```json
{
  "repo_name": "example-repo",
  "repo_path": "/home/user/repos/example-repo",
  "is_git_repo": true,
  "has_uncommitted_changes": true,
  "uncommitted_files": ["README.md", "src/main.py"],
  "is_up_to_date_with_remote": false,
  "has_unpushed_commits": true,
  "unpushed_commit_count": 2,
  "scan_timestamp": "2026-05-19T00:00:00Z"
}
```

## Proposed Components

- `collector.py`: directory traversal and orchestration.
- `git_state.py`: Git status extraction logic.
- `output.py`: JSONL persistence.
- `app.py`: FastAPI endpoints and local presentation.
- `docker-compose.yml`: local service orchestration.

## Operational Flow

1. Trigger scan.
2. Walk `~/repos` subdirectories.
3. Capture Git status per repository.
4. Write/update JSONL output.
5. FastAPI serves current status view from JSONL.

## Deployment Expectations

- Local environment uses `uv` for Python project management.
- `docker compose up` should be the primary deployment/start command.
- Runtime data file should be mounted/preserved as needed for local use.

## Current Scope of This Repository Change

This change defines project documentation and specification only.
No implementation logic is introduced in this step.
