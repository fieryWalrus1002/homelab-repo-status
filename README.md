# homelab-repo-status

Scans local Git repositories under `~/repos`, persists status to a JSONL file, and exposes the data via a FastAPI service. Alerts on dirty repos via Slack and/or ntfy.

## Project layout

```
homelab-repo-status/
├── src/homelab_repo_status/
│   ├── collector.py      # walks REPOS_DIR and gathers git state per repo
│   ├── git_state.py      # git status helpers with per-command timing logs
│   ├── output.py         # JSONL read/write
│   ├── alert.py          # rotating-log alerting + Slack/ntfy delivery
│   ├── config.py         # loads config.yml with defaults
│   ├── cli.py            # homelab-repo-status CLI
│   └── app.py            # FastAPI app
├── data/
│   └── repo_status.jsonl
├── config.yml            # tunable parameters
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
| POST | `/alert` | Scan, persist, and fire batched alerts for any dirty repos |

## Alert delivery

Alerts are batched into a single message per scan. Delivery channels are opt-in via env vars:

- **Slack** — set `SLACK_WEBHOOK_URL`. Bot name and icon are configurable.
- **ntfy.sh** — set `NTFY_TOPIC`. Works with the ntfy mobile app; self-hostable.
- **Log file** — always written regardless of other channels.

## Running

```bash
cp .env.example .env   # fill in secrets
docker compose up -d
```

Service runs on port `8086`. Repos are mounted from `REPOS_DIR` (read-write, required for `git fetch`).

Swagger UI available at `http://localhost:8086/docs`.

## Configuration

Tunable parameters live in `config.yml` (mounted into the container, no rebuild needed to change):

```yaml
git:
  command_timeout: 5  # seconds; applies to each git subprocess (fetch, status, rev-parse, etc.)
```

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `REPOS_DIR` | `~/repos` | Directory to scan |
| `DATA_DIR` | `/app/data` | Where `repo_status.jsonl` is written |
| `CONFIG_PATH` | `config.yml` | Path to config file |
| `LOG_LEVEL` | `INFO` | Log verbosity (`DEBUG` shows per-command git timing) |
| `SLACK_WEBHOOK_URL` | _(unset)_ | Slack incoming webhook URL |
| `SLACK_USERNAME` | `homelab-repo-status` | Slack bot display name |
| `SLACK_ICON_EMOJI` | `:house:` | Slack bot icon |
| `NTFY_TOPIC` | _(unset)_ | ntfy.sh topic name |
| `HOMELAB_REPO_STATUS_ALERT_LOG` | `homelab_repo_status_alerts.log` | Alert log path (docker-compose sets `/app/data/alerts.log`) |

## Cron usage

`POST /alert` is designed to be called on a schedule:

```bash
# alert on dirty repos every morning at 8am
0 8 * * * curl -s -X POST http://localhost:8086/alert
```
