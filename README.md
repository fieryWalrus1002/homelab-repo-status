# homelab-repo-status

A bare-bones Python **uv** project plan for collecting local Git repository status from `~/repos`, writing results to a JSONL file, and serving that data through a local FastAPI app.

## What this project is for

This project is intended to:
- Scan each subdirectory in `~/repos`
- Detect Git state per repository, including:
  - uncommitted files
  - whether local is up to date with remote
  - local commits not pushed yet
  - local files not committed
- Persist repository status records to a JSONL file
- Expose the data via a local FastAPI web app
- Run the stack with Docker Compose

## Bare-bones project layout

```text
homelab-repo-status/
├── README.md
├── specs/
│   └── project.md
├── pyproject.toml            # uv-managed Python project config
├── src/
│   └── homelab_repo_status/
│       ├── collector.py      # walks ~/repos and gathers git status per repo
│       ├── git_state.py      # git status helpers/checks
│       ├── output.py         # JSONL writing/reading
│       └── app.py            # FastAPI app serving status data
├── data/
│   └── repo_status.jsonl     # generated output
└── docker-compose.yml        # local app orchestration
```

## Data contract (JSONL)

Each line should be a JSON object representing one repository scan result.

Suggested fields:
- `repo_name`
- `repo_path`
- `is_git_repo`
- `has_uncommitted_changes`
- `uncommitted_files`
- `is_up_to_date_with_remote`
- `has_unpushed_commits`
- `unpushed_commit_count`
- `scan_timestamp`

## Deployment model

- Local-first development with **uv**
- Local API hosting with **FastAPI**
- Service startup via `docker compose up`

## Status

This repository currently documents the intended structure and goals only.
Implementation code is intentionally not included in this step.
