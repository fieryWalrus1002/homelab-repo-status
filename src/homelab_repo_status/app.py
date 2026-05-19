import logging
import os

from fastapi import BackgroundTasks, FastAPI, HTTPException

from homelab_repo_status.collector import collect
from homelab_repo_status.output import read_records, write_records
from homelab_repo_status.alert import alert_message, is_problematic, trigger_batch

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

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
    background_tasks.add_task(_fire_alerts, problems)
    return {"scanned": len(records), "alerted": len(problems)}