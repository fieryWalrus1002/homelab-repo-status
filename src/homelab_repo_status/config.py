import os
from pathlib import Path

import yaml

_DEFAULTS = {
    "git": {
        "command_timeout": 5,
    },
}


def _validate_config(data) -> dict:
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError("config.yml must contain a YAML mapping at the top level")
    if "git" in data and not isinstance(data["git"], dict):
        raise ValueError("config.yml key 'git' must contain a YAML mapping")
    return data


def _load() -> dict:
    path = Path(os.getenv("CONFIG_PATH", "config.yml"))
    if not path.exists():
        return _DEFAULTS
    with path.open() as f:
        data = _validate_config(yaml.safe_load(f))
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
