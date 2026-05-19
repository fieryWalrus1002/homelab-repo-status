from unittest.mock import MagicMock, patch


from homelab_repo_status.alert import Alert, alert_message, is_problematic


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
        assert is_problematic(
            _record(has_uncommitted_changes=True, uncommitted_files=["f.py"])
        )

    def test_unpushed_commits(self):
        assert is_problematic(
            _record(has_unpushed_commits=True, unpushed_commit_count=1)
        )

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


class TestAlertTrigger:
    def test_logs_message(self):
        with patch("homelab_repo_status.alert.logger") as mock_logger:
            Alert("test message").trigger()
        mock_logger.info.assert_called_once()
        assert "test message" in mock_logger.info.call_args[0][0]

    def test_ntfy_skipped_when_no_topic(self):
        with patch.dict("os.environ", {}, clear=True):
            with patch(
                "homelab_repo_status.alert.urllib.request.urlopen"
            ) as mock_urlopen:
                Alert("msg").trigger()
        mock_urlopen.assert_not_called()

    def test_ntfy_posts_when_topic_set(self):
        with patch.dict("os.environ", {"NTFY_TOPIC": "my-topic"}):
            with patch(
                "homelab_repo_status.alert.urllib.request.urlopen"
            ) as mock_urlopen:
                mock_urlopen.return_value = MagicMock()
                Alert("msg").trigger()
        assert any(
            "ntfy.sh/my-topic" in str(call.args[0].full_url)
            for call in mock_urlopen.call_args_list
        )

    def test_slack_skipped_when_no_webhook(self):
        with patch.dict("os.environ", {}, clear=True):
            with patch(
                "homelab_repo_status.alert.urllib.request.urlopen"
            ) as mock_urlopen:
                Alert("msg").trigger()
        mock_urlopen.assert_not_called()

    def test_slack_posts_when_webhook_set(self):
        webhook = "https://hooks.slack.com/services/xxx/yyy/zzz"
        with patch.dict("os.environ", {"SLACK_WEBHOOK_URL": webhook}):
            with patch(
                "homelab_repo_status.alert.urllib.request.urlopen"
            ) as mock_urlopen:
                mock_urlopen.return_value = MagicMock()
                Alert("msg").trigger()
        assert any(
            webhook in str(call.args[0].full_url)
            for call in mock_urlopen.call_args_list
        )

    def test_slack_failure_does_not_raise(self):
        webhook = "https://hooks.slack.com/services/xxx/yyy/zzz"
        with patch.dict("os.environ", {"SLACK_WEBHOOK_URL": webhook}):
            with patch(
                "homelab_repo_status.alert.urllib.request.urlopen",
                side_effect=Exception("network error"),
            ):
                Alert("msg").trigger()  # should not raise
