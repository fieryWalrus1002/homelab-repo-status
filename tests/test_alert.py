import pytest

from homelab_repo_status.alert import alert_message, is_problematic


def _record(**kwargs) -> dict:
    base = {
        "repo_name": "test-repo",
        "has_uncommitted_changes": False,
        "uncommitted_files": [],
        "is_up_to_date_with_remote": True,
        "has_unpushed_commits": False,
        "unpushed_commit_count": 0,
    }
    base.update(kwargs)
    return base


class TestIsProblematic:
    def test_clean_repo(self):
        assert not is_problematic(_record())

    def test_uncommitted_changes(self):
        assert is_problematic(_record(has_uncommitted_changes=True, uncommitted_files=["f.py"]))

    def test_unpushed_commits(self):
        assert is_problematic(_record(has_unpushed_commits=True, unpushed_commit_count=1))

    def test_behind_remote(self):
        assert is_problematic(_record(is_up_to_date_with_remote=False))


class TestAlertMessage:
    def test_includes_repo_name(self):
        r = _record(has_uncommitted_changes=True, uncommitted_files=["a.py"])
        assert "test-repo" in alert_message(r)

    def test_uncommitted_file_count(self):
        r = _record(has_uncommitted_changes=True, uncommitted_files=["a.py", "b.py"])
        assert "2" in alert_message(r)

    def test_unpushed_commit_count(self):
        r = _record(has_unpushed_commits=True, unpushed_commit_count=3)
        assert "3" in alert_message(r)

    def test_behind_remote_label(self):
        r = _record(is_up_to_date_with_remote=False)
        assert "behind" in alert_message(r)
