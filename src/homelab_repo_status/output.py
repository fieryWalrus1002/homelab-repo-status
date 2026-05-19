import json
import os
from pathlib import Path

_default_data_dir = Path(__file__).parent.parent.parent / "data"


def _jsonl_path() -> Path:
    data_dir = Path(os.environ.get("DATA_DIR", str(_default_data_dir)))
    return data_dir / "repo_status.jsonl"


def write_records(records: list[dict], path: Path | None = None) -> None:
    target = path or _jsonl_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "w") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")


def read_records(path: Path | None = None) -> list[dict]:
    target = path or _jsonl_path()
    if not target.exists():
        return []
    records = []
    with open(target) as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records
