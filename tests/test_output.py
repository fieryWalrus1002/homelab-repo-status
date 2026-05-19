import json

import pytest

from homelab_repo_status.output import read_records, write_records


RECORDS = [
    {"repo_name": "foo", "is_git_repo": True, "scan_timestamp": "2026-05-19T00:00:00+00:00"},
    {"repo_name": "bar", "is_git_repo": False, "scan_timestamp": "2026-05-19T00:00:00+00:00"},
]


class TestWriteRecords:
    def test_one_json_object_per_line(self, tmp_path):
        path = tmp_path / "status.jsonl"
        write_records(RECORDS, path)
        lines = [l for l in path.read_text().splitlines() if l.strip()]
        assert len(lines) == 2
        for line in lines:
            json.loads(line)  # each line must be valid JSON

    def test_creates_missing_parent_directories(self, tmp_path):
        path = tmp_path / "nested" / "deep" / "status.jsonl"
        write_records(RECORDS, path)
        assert path.exists()

    def test_overwrites_existing_content(self, tmp_path):
        path = tmp_path / "status.jsonl"
        write_records(RECORDS, path)
        write_records([RECORDS[0]], path)
        assert len(read_records(path)) == 1


class TestReadRecords:
    def test_roundtrip(self, tmp_path):
        path = tmp_path / "status.jsonl"
        write_records(RECORDS, path)
        assert read_records(path) == RECORDS

    def test_returns_empty_list_for_missing_file(self, tmp_path):
        assert read_records(tmp_path / "nonexistent.jsonl") == []

    def test_skips_blank_lines(self, tmp_path):
        path = tmp_path / "status.jsonl"
        path.write_text('{"repo_name": "foo"}\n\n{"repo_name": "bar"}\n')
        assert len(read_records(path)) == 2
