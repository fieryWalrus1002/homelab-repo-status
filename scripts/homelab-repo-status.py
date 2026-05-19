#!/usr/bin/env python3
import os
import sys

os.execvp(
    "uv",
    [
        "uv",
        "run",
        "--project",
        os.path.join(os.path.expanduser("~"), "repos", "homelab-repo-status"),
        "homelab-repo-status",
        *sys.argv[1:],
    ],
)
