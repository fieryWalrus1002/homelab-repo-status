from fastapi import FastAPI, HTTPException

from homelab_repo_status.collector import collect
from homelab_repo_status.output import read_records, write_records
from homelab_repo_status.alert import Alert


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


@app.post("/alert")
def trigger_alert() -> dict:
    # STUB: This is where the logic for determining if an alert should be triggered would go. 
    # For example, maybe theres a ton of work done that isn't commited, or maybe there are some
    # known vulnerabilities in the dependencies. This is where the logic for determining if an alert
    # should be triggered would go.
    alert = Alert("This is a test alert. Replace with real logic to determine when to trigger an alert.")
    alert.trigger()
    return {"alert": "Triggered"}


# Need some endpoitns for the ~/.local/bin/homelab-repo-status script to call:
# 
# 1. performa a scan, and return the results as a pretty printed table summary
# 2. perform a scan, and then trigger an alert if any repositories are found to be in a "bad" state (e.g., outdated, vulnerable, etc.)