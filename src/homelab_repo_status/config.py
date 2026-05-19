import os
from pathlib import Path

import yaml

_DEFAULTS = {
    "git": {
        "fetch_timeout": 5,
    },
}


def _load() -> dict:
    path = Path(os.getenv("CONFIG_PATH", "config.yml"))
    if not path.exists():
        return _DEFAULTS
    with path.open() as f:
        data = yaml.safe_load(f) or {}
    return _merge(_DEFAULTS, data)


def _merge(base: dict, override: dict) -> dict:
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _merge(result[key], value)
        else:
            result[key] = value
    return result


config = _load()
