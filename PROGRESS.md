# Implementation Progress

## Done

- [x] Project structure — uv, src layout, `pyproject.toml`
- [x] `git_state.py` — detect uncommitted changes, unpushed commits, remote sync status
- [x] `output.py` — JSONL write/read with configurable path via `DATA_DIR`
- [x] `collector.py` — walk `~/repos` subdirectories, build records, `collect` CLI entry point
- [x] `app.py` — FastAPI with `GET /status`, `GET /status/{repo_name}`, `POST /scan`, `POST /alert`
- [x] `alert.py` — batched Slack + ntfy delivery, rotating log, `is_problematic`, `alert_message`
- [x] `cli.py` — `scan` (pretty table) and `check` (scan + alert on problems) subcommands
- [x] `config.py` — `config.yml` loader with validation and defaults
- [x] `Dockerfile` + `docker-compose.yml` — local containerised deployment
- [x] `scripts/pre-commit` + `.github/workflows/ci.yml` — ruff lint/format + pytest on commit and PR
- [x] Test suite — 37 tests across `git_state`, `output`, `collector`, `alert`, `app`, `cli`
- [x] Docker Compose validated end-to-end — scan and alert confirmed working

## Outstanding

- [ ] **Alert enable/disable API** — `POST /alert/enable`, `POST /alert/disable`, `GET /alert/status`
- [ ] **Slack bidirectional integration** — receive commands from Slack (see issue; likely a separate homelab-slack-gateway repo)
- [ ] **Authentication** — no auth on `POST /alert` / `POST /scan`; tracked issue for when service is exposed beyond localhost
- [ ] **Safer git directory handling** — scope `safe.directory` or run container as non-root; tracked issue
- [ ] **Web UI** — API-only right now; an HTML status table would make the app self-contained
- [ ] **Repo exclusion list** — non-git dirs show up in scans; add a skip list

## Nice to Have

- [ ] Configurable alert thresholds (e.g. only alert after N uncommitted files)
- [ ] Historical JSONL data — keep per-scan snapshots rather than overwriting
