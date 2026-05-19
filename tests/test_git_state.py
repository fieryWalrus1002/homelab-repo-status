from unittest.mock import MagicMock, patch

from homelab_repo_status.git_state import get_git_state


def _proc(returncode: int = 0, stdout: str = "") -> MagicMock:
    m = MagicMock()
    m.returncode = returncode
    m.stdout = stdout
    return m


class TestGetGitState:
    def test_non_git_directory(self, tmp_path):
        with patch("homelab_repo_status.git_state.subprocess.run") as mock_run:
            mock_run.return_value = _proc(128)
            state = get_git_state(tmp_path)

        assert not state.is_git_repo
        assert not state.has_uncommitted_changes
        assert state.uncommitted_files == []
        assert state.is_up_to_date_with_remote
        assert not state.has_unpushed_commits
        assert state.unpushed_commit_count == 0

    def test_clean_repo_in_sync_with_remote(self, tmp_path):
        with patch("homelab_repo_status.git_state.subprocess.run") as mock_run:
            mock_run.side_effect = [
                _proc(0, "true"),  # rev-parse
                _proc(0, ""),  # status --porcelain
                _proc(0),  # fetch
                _proc(0, "0\t0"),  # rev-list ahead/behind
            ]
            state = get_git_state(tmp_path)

        assert state.is_git_repo
        assert not state.has_uncommitted_changes
        assert state.uncommitted_files == []
        assert state.is_up_to_date_with_remote
        assert not state.has_unpushed_commits
        assert state.unpushed_commit_count == 0

    def test_uncommitted_changes(self, tmp_path):
        with patch("homelab_repo_status.git_state.subprocess.run") as mock_run:
            mock_run.side_effect = [
                _proc(0, "true"),
                _proc(0, " M README.md\n?? new_file.py"),
                _proc(0),
                _proc(0, "0\t0"),
            ]
            state = get_git_state(tmp_path)

        assert state.has_uncommitted_changes
        assert state.uncommitted_files == ["README.md", "new_file.py"]
        assert state.is_up_to_date_with_remote

    def test_unpushed_commits(self, tmp_path):
        with patch("homelab_repo_status.git_state.subprocess.run") as mock_run:
            mock_run.side_effect = [
                _proc(0, "true"),
                _proc(0, ""),
                _proc(0),
                _proc(0, "0\t3"),  # 3 commits ahead
            ]
            state = get_git_state(tmp_path)

        assert not state.is_up_to_date_with_remote
        assert state.has_unpushed_commits
        assert state.unpushed_commit_count == 3

    def test_behind_remote(self, tmp_path):
        with patch("homelab_repo_status.git_state.subprocess.run") as mock_run:
            mock_run.side_effect = [
                _proc(0, "true"),
                _proc(0, ""),
                _proc(0),
                _proc(0, "2\t0"),  # 2 commits behind
            ]
            state = get_git_state(tmp_path)

        assert not state.is_up_to_date_with_remote
        assert not state.has_unpushed_commits
        assert state.unpushed_commit_count == 0

    def test_no_upstream_tracking_branch(self, tmp_path):
        with patch("homelab_repo_status.git_state.subprocess.run") as mock_run:
            mock_run.side_effect = [
                _proc(0, "true"),
                _proc(0, ""),
                _proc(0),
                _proc(128, ""),  # rev-list fails — no upstream configured
            ]
            state = get_git_state(tmp_path)

        assert state.is_git_repo
        assert state.is_up_to_date_with_remote
        assert not state.has_unpushed_commits
        assert state.unpushed_commit_count == 0
