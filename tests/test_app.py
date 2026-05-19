from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from homelab_repo_status.app import app


RECORDS = [
    {
        "repo_name": "repo-a",
        "repo_path": "/repos/repo-a",
        "is_git_repo": True,
        "has_uncommitted_changes": False,
        "uncommitted_files": [],
        "is_up_to_date_with_remote": True,
        "has_unpushed_commits": False,
        "unpushed_commit_count": 0,
        "scan_timestamp": "2026-05-19T00:00:00+00:00",
    },
    {
        "repo_name": "repo-b",
        "repo_path": "/repos/repo-b",
        "is_git_repo": True,
        "has_uncommitted_changes": True,
        "uncommitted_files": ["file.py"],
        "is_up_to_date_with_remote": False,
        "has_unpushed_commits": True,
        "unpushed_commit_count": 2,
        "scan_timestamp": "2026-05-19T00:00:00+00:00",
    },
]


@pytest.fixture
def client():
    return TestClient(app)


class TestGetAllStatus:
    def test_returns_all_records(self, client):
        with patch("homelab_repo_status.app.read_records", return_value=RECORDS):
            r = client.get("/status")
        assert r.status_code == 200
        assert len(r.json()) == 2

    def test_empty_when_no_records(self, client):
        with patch("homelab_repo_status.app.read_records", return_value=[]):
            r = client.get("/status")
        assert r.status_code == 200
        assert r.json() == []


class TestGetRepoStatus:
    def test_returns_matching_record(self, client):
        with patch("homelab_repo_status.app.read_records", return_value=RECORDS):
            r = client.get("/status/repo-a")
        assert r.status_code == 200
        assert r.json()["repo_name"] == "repo-a"

    def test_404_for_unknown_repo(self, client):
        with patch("homelab_repo_status.app.read_records", return_value=RECORDS):
            r = client.get("/status/nonexistent")
        assert r.status_code == 404

    def test_404_detail_includes_repo_name(self, client):
        with patch("homelab_repo_status.app.read_records", return_value=[]):
            r = client.get("/status/missing-repo")
        assert "missing-repo" in r.json()["detail"]


class TestTriggerScan:
    def test_returns_scanned_count(self, client):
        with (
            patch("homelab_repo_status.app.collect", return_value=RECORDS),
            patch("homelab_repo_status.app.write_records"),
        ):
            r = client.post("/scan")
        assert r.status_code == 200
        assert r.json() == {"scanned": 2}


class TestTriggerAlert:
    def test_returns_scanned_and_alerted_counts(self, client):
        with (
            patch("homelab_repo_status.app.collect", return_value=RECORDS),
            patch("homelab_repo_status.app.write_records"),
            patch("homelab_repo_status.alert.urllib.request.urlopen"),
        ):
            r = client.post("/alert")
        assert r.status_code == 200
        assert r.json() == {"scanned": 2, "alerted": 1}

    def test_alerted_zero_when_all_clean(self, client):
        clean = [RECORDS[0]]
        with (
            patch("homelab_repo_status.app.collect", return_value=clean),
            patch("homelab_repo_status.app.write_records"),
        ):
            r = client.post("/alert")
        assert r.status_code == 200
        assert r.json() == {"scanned": 1, "alerted": 0}
