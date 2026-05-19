import logging
import os

from fastapi import BackgroundTasks, FastAPI, HTTPException

from homelab_repo_status.alert import alert_message, is_problematic, trigger_batch
from homelab_repo_status.collector import collect
from homelab_repo_status.output import read_records, write_records

# basicConfig is a no-op under Uvicorn (it configures the root logger first).
# Configure our package logger explicitly so LOG_LEVEL is always respected.
_pkg_logger = logging.getLogger("homelab_repo_status")
_pkg_logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())
if not _pkg_logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    )
    _pkg_logger.addHandler(_handler)
_pkg_logger.propagate = False

app = FastAPI(title="homelab-repo-status", version="0.1.0")


@app.get("/status")
def get_all_status() -> list[dict]:
    return read_records()


@app.get("/status/{repo_name}")
def get_repo_status(repo_name: str) -> dict:
    for record in read_records():
        if record.get("repo_name") == repo_name:
            return record
    raise HTTPException(status_code=404, detail=f"Repository '{repo_name}' not found")


@app.post("/scan")
def trigger_scan() -> dict:
    records = collect()
    write_records(records)
    return {"scanned": len(records)}


def _fire_alerts(problems: list[dict]) -> None:
    trigger_batch([alert_message(repo) for repo in problems])


@app.post("/alert")
def trigger_alert(background_tasks: BackgroundTasks) -> dict:
    records = collect()
    write_records(records)
    problems = [r for r in records if is_problematic(r)]
    if problems:
        background_tasks.add_task(_fire_alerts, problems)
    return {"scanned": len(records), "alerted": len(problems)}
