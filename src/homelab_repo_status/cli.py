import argparse
import sys

from homelab_repo_status.alert import Alert, alert_message, is_problematic
from homelab_repo_status.collector import collect
from homelab_repo_status.output import write_records


def cmd_scan(_args: argparse.Namespace) -> None:
    records = collect()
    write_records(records)
    _print_table(records)


def cmd_check(_args: argparse.Namespace) -> None:
    records = collect()
    write_records(records)

    problems = [r for r in records if is_problematic(r)]
    if not problems:
        print("All repositories are clean.")
        return

    for repo in problems:
        Alert(alert_message(repo)).trigger()

    print(f"Alerted on {len(problems)} repositor{'y' if len(problems) == 1 else 'ies'}.")
    sys.exit(1)


def _print_table(records: list[dict]) -> None:
    if not records:
        print("No repositories found.")
        return

    col_widths = {
        "repo": max(len("REPO"), max(len(r["repo_name"]) for r in records)),
        "git": 3,
        "uncommitted": max(len("UNCOMMITTED"), 11),
        "unpushed": max(len("UNPUSHED"), 8),
        "in_sync": len("IN SYNC"),
    }

    def row(repo, git, uncommitted, unpushed, in_sync):
        return (
            f"{repo:<{col_widths['repo']}}  "
            f"{git:<{col_widths['git']}}  "
            f"{uncommitted:<{col_widths['uncommitted']}}  "
            f"{unpushed:<{col_widths['unpushed']}}  "
            f"{in_sync}"
        )

    header = row("REPO", "GIT", "UNCOMMITTED", "UNPUSHED", "IN SYNC")
    separator = "-" * len(header)
    print(header)
    print(separator)

    for r in records:
        if not r["is_git_repo"]:
            print(row(r["repo_name"], "no", "-", "-", "-"))
            continue

        uncommitted = f"{len(r['uncommitted_files'])} file(s)" if r["has_uncommitted_changes"] else "clean"
        unpushed = str(r["unpushed_commit_count"]) if r["has_unpushed_commits"] else "0"
        in_sync = "yes" if r["is_up_to_date_with_remote"] else "no"
        print(row(r["repo_name"], "yes", uncommitted, unpushed, in_sync))


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="homelab-repo-status",
        description="Scan local Git repositories and report their status.",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("scan", help="Scan repos and print a status table")
    sub.add_parser("check", help="Scan repos and alert on any with issues")

    args = parser.parse_args()
    {"scan": cmd_scan, "check": cmd_check}[args.command](args)
