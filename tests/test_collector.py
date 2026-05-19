from unittest.mock import patch


from homelab_repo_status.collector import collect
from homelab_repo_status.git_state import GitState


def _state(**kwargs) -> GitState:
    defaults = dict(
        is_git_repo=True,
        has_uncommitted_changes=False,
        uncommitted_files=[],
        is_up_to_date_with_remote=True,
        has_unpushed_commits=False,
        unpushed_commit_count=0,
    )
    defaults.update(kwargs)
    return GitState(**defaults)


CLEAN = _state()
NOT_GIT = _state(is_git_repo=False)


class TestCollect:
    def test_one_record_per_subdirectory(self, tmp_path):
        (tmp_path / "repo-a").mkdir()
        (tmp_path / "repo-b").mkdir()

        with patch("homelab_repo_status.collector.get_git_state", return_value=CLEAN):
            records = collect(tmp_path)

        assert len(records) == 2

    def test_ignores_files_at_top_level(self, tmp_path):
        (tmp_path / "repo-a").mkdir()
        (tmp_path / "stray.txt").write_text("ignored")

        with patch("homelab_repo_status.collector.get_git_state", return_value=CLEAN):
            records = collect(tmp_path)

        assert len(records) == 1

    def test_record_shape(self, tmp_path):
        (tmp_path / "my-repo").mkdir()

        with patch("homelab_repo_status.collector.get_git_state", return_value=CLEAN):
            records = collect(tmp_path)

        r = records[0]
        assert r["repo_name"] == "my-repo"
        assert r["repo_path"] == str(tmp_path / "my-repo")
        assert r["is_git_repo"] is True
        assert "scan_timestamp" in r

    def test_non_git_directory_reflected_in_record(self, tmp_path):
        (tmp_path / "not-a-repo").mkdir()

        with patch("homelab_repo_status.collector.get_git_state", return_value=NOT_GIT):
            records = collect(tmp_path)

        assert records[0]["is_git_repo"] is False

    def test_repos_sorted_alphabetically(self, tmp_path):
        for name in ["zebra", "apple", "mango"]:
            (tmp_path / name).mkdir()

        with patch("homelab_repo_status.collector.get_git_state", return_value=CLEAN):
            records = collect(tmp_path)

        assert [r["repo_name"] for r in records] == ["apple", "mango", "zebra"]
