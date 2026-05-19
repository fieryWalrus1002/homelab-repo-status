import json
import logging
import os
import urllib.request
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__name__)


def _configure_logger() -> None:
    logger.setLevel(logging.INFO)
    logger.propagate = False

    log_path = os.getenv("HOMELAB_REPO_STATUS_ALERT_LOG", "homelab_repo_status_alerts.log")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    for existing_handler in logger.handlers:
        if isinstance(existing_handler, RotatingFileHandler) and getattr(existing_handler, "baseFilename", None) == os.path.abspath(log_path):
            existing_handler.setFormatter(formatter)
            return

    handler = RotatingFileHandler(log_path, maxBytes=1048576, backupCount=3)
    handler.setFormatter(formatter)
    logger.addHandler(handler)


_configure_logger()


def _ntfy(message: str) -> None:
    topic = os.getenv("NTFY_TOPIC")
    if not topic:
        return
    try:
        req = urllib.request.Request(
            f"https://ntfy.sh/{topic}",
            data=message.encode(),
            method="POST",
            headers={"Title": "homelab-repo-status"},
        )
        urllib.request.urlopen(req, timeout=5)
    except Exception as e:
        logger.warning(f"ntfy delivery failed: {e}")


def _slack(message: str) -> None:
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        return
    try:
        payload = json.dumps({
            "text": message,
            "username": os.getenv("SLACK_USERNAME", "homelab-repo-status"),
            "icon_emoji": os.getenv("SLACK_ICON_EMOJI", ":house:"),
        }).encode()
        req = urllib.request.Request(
            webhook_url,
            data=payload,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        urllib.request.urlopen(req, timeout=5)
    except Exception as e:
        logger.warning(f"Slack delivery failed: {e}")


class Alert:
    def __init__(self, message: str):
        self.message = message

    def trigger(self) -> None:
        logger.info(f"ALERT: {self.message}")
        _ntfy(self.message)
        _slack(self.message)


def is_problematic(record: dict) -> bool:
    return (
        record.get("has_uncommitted_changes", False)
        or record.get("has_unpushed_commits", False)
        or not record.get("is_up_to_date_with_remote", True)
    )


def alert_message(record: dict) -> str:
    issues = []
    if record.get("has_uncommitted_changes"):
        count = len(record.get("uncommitted_files", []))
        issues.append(f"{count} uncommitted file(s)")
    if record.get("has_unpushed_commits"):
        issues.append(f"{record.get('unpushed_commit_count', 0)} unpushed commit(s)")
    if not record.get("is_up_to_date_with_remote") and not record.get("has_unpushed_commits"):
        issues.append("behind remote")
    return f"{record['repo_name']}: {', '.join(issues)}"
