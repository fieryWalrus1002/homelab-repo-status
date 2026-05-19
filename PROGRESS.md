# Implementation Progress

## Done

- [x] Project structure — uv, src layout, `pyproject.toml`
- [x] `git_state.py` — detect uncommitted changes, unpushed commits, remote sync status
- [x] `output.py` — JSONL write/read with configurable path via `DATA_DIR`
- [x] `collector.py` — walk `~/repos` subdirectories, build records, `collect` CLI entry point
- [x] `app.py` — FastAPI with `GET /status`, `GET /status/{repo_name}`, `POST /scan`
- [x] `alert.py` — `Alert` class, `is_problematic`, `alert_message` helpers
- [x] `cli.py` — `scan` (pretty table) and `check` (scan + alert on problems) subcommands
- [x] `Dockerfile` + `docker-compose.yml` — local containerised deployment
- [x] `scripts/homelab-repo-status.py` — bash entry point via `uv run`
- [x] `~/.local/bin` symlink — single stable path for terminal and cron use
- [x] Test suite — 37 tests across `git_state`, `output`, `collector`, `alert`, `app`, `cli`

## Outstanding

- [ ] **Alert delivery** — `Alert.trigger()` only logs to file; wire up email or push notification
- [ ] **`POST /alert` endpoint** — currently a hardcoded stub; needs real detection logic
- [ ] **Docker Compose validation** — images build and compose file exists, but not tested end-to-end
- [ ] **Web UI** — API-only right now; an HTML status table would make the app self-contained
- [ ] **Repo exclusion list** — non-git dirs (e.g. scratch folders) show up in scans; add a skip list
- [ ] **Cron setup guide** — document the full cron + symlink deployment steps in the README

## Nice to Have

- [ ] Configurable alert thresholds (e.g. only alert after N uncommitted files)
- [ ] Dependency vulnerability scanning as an alert trigger
- [ ] Historical JSONL data — keep per-scan snapshots rather than overwriting
