import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler("homelab_repo_status_alerts.log")
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)


class Alert:
    def __init__(self, message: str):
        self.message = message

    def trigger(self) -> None:
        logger.info(f"ALERT: {self.message}")


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
