#!/usr/bin/env bash
set -eo pipefail

exec uv run --project "$HOME/repos/homelab-repo-status" homelab-repo-status "$@"
