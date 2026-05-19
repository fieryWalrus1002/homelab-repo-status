FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/* \
    && git config --global --add safe.directory '*'

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./

COPY src/ ./src/

RUN uv sync --no-dev

ENV PATH="/app/.venv/bin:$PATH"
ENV DATA_DIR="/app/data"

EXPOSE 8000

CMD ["uvicorn", "homelab_repo_status.app:app", "--host", "0.0.0.0", "--port", "8000"]
