from unittest.mock import patch

import pytest

from homelab_repo_status.cli import main

PROBLEM_RECORDS = [
    {
        "repo_name": "my-repo",
        "repo_path": "/repos/my-repo",
        "is_git_repo": True,
        "has_uncommitted_changes": True,
        "uncommitted_files": ["README.md"],
        "is_up_to_date_with_remote": True,
        "has_unpushed_commits": False,
        "unpushed_commit_count": 0,
        "scan_timestamp": "2026-05-19T00:00:00+00:00",
    }
]

CLEAN_RECORDS = [
    {
        "repo_name": "my-repo",
        "repo_path": "/repos/my-repo",
        "is_git_repo": True,
        "has_uncommitted_changes": False,
        "uncommitted_files": [],
        "is_up_to_date_with_remote": True,
        "has_unpushed_commits": False,
        "unpushed_commit_count": 0,
        "scan_timestamp": "2026-05-19T00:00:00+00:00",
    }
]


class TestScanCommand:
    def test_prints_table_header(self, capsys):
        with (
            patch("homelab_repo_status.cli.collect", return_value=PROBLEM_RECORDS),
            patch("homelab_repo_status.cli.write_records"),
            patch("sys.argv", ["homelab-repo-status", "scan"]),
        ):
            main()

        out = capsys.readouterr().out
        assert "REPO" in out
        assert "UNCOMMITTED" in out
        assert "IN SYNC" in out

    def test_prints_repo_name_in_row(self, capsys):
        with (
            patch("homelab_repo_status.cli.collect", return_value=PROBLEM_RECORDS),
            patch("homelab_repo_status.cli.write_records"),
            patch("sys.argv", ["homelab-repo-status", "scan"]),
        ):
            main()

        assert "my-repo" in capsys.readouterr().out

    def test_empty_repos_prints_message(self, capsys):
        with (
            patch("homelab_repo_status.cli.collect", return_value=[]),
            patch("homelab_repo_status.cli.write_records"),
            patch("sys.argv", ["homelab-repo-status", "scan"]),
        ):
            main()

        assert "No repositories found" in capsys.readouterr().out


class TestCheckCommand:
    def test_exits_0_when_all_clean(self):
        with (
            patch("homelab_repo_status.cli.collect", return_value=CLEAN_RECORDS),
            patch("homelab_repo_status.cli.write_records"),
            patch("homelab_repo_status.cli.Alert"),
            patch("sys.argv", ["homelab-repo-status", "check"]),
        ):
            main()  # must not raise

    def test_exits_1_when_problems_found(self):
        with (
            patch("homelab_repo_status.cli.collect", return_value=PROBLEM_RECORDS),
            patch("homelab_repo_status.cli.write_records"),
            patch("homelab_repo_status.cli.Alert"),
            patch("sys.argv", ["homelab-repo-status", "check"]),
            pytest.raises(SystemExit) as exc_info,
        ):
            main()

        assert exc_info.value.code == 1

    def test_fires_alert_per_problem_repo(self):
        with (
            patch("homelab_repo_status.cli.collect", return_value=PROBLEM_RECORDS),
            patch("homelab_repo_status.cli.write_records"),
            patch("homelab_repo_status.cli.Alert") as mock_alert_cls,
            patch("sys.argv", ["homelab-repo-status", "check"]),
            pytest.raises(SystemExit),
        ):
            main()

        mock_alert_cls.assert_called_once()
        mock_alert_cls.return_value.trigger.assert_called_once()
