# homelab-repo-status

Scans local Git repositories under `~/repos`, persists status to a JSONL file, and exposes the data via a FastAPI service.

## Project layout

```
homelab-repo-status/
├── src/homelab_repo_status/
│   ├── collector.py      # walks REPOS_DIR and gathers git state per repo
│   ├── git_state.py      # git status helpers
│   ├── output.py         # JSONL read/write
│   ├── alert.py          # rotating-log alerting
│   ├── cli.py            # homelab-repo-status CLI
│   └── app.py            # FastAPI app
├── data/
│   └── repo_status.jsonl
├── main.py               # CLI entrypoint
└── docker-compose.yml
```

## CLI

```
homelab-repo-status scan    # scan repos and print a status table
homelab-repo-status check   # scan repos and alert on any with issues (exits 1 if any found)
```

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/status` | All repo records |
| GET | `/status/{repo_name}` | Single repo record |
| POST | `/scan` | Trigger a scan and persist results |

## Running

```bash
docker compose up
```

Service runs on port `8086`. Repos are mounted read-only from `REPOS_DIR`.

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `REPOS_DIR` | `~/repos` | Directory to scan |
| `DATA_DIR` | `/app/data` | Where `repo_status.jsonl` is written |
| `HOMELAB_REPO_STATUS_ALERT_LOG` | `homelab_repo_status_alerts.log` | Alert log path |
| `NTFY_TOPIC` | _(unset)_ | ntfy.sh topic to push alerts to (optional) |
| `SLACK_WEBHOOK_URL` | _(unset)_ | Slack incoming webhook URL (optional) |
