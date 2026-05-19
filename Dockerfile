FROM python:3.13-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml ./
COPY src/ ./src/

RUN uv sync --no-dev

ENV PATH="/app/.venv/bin:$PATH"
ENV DATA_DIR="/app/data"

EXPOSE 8000

CMD ["uvicorn", "homelab_repo_status.app:app", "--host", "0.0.0.0", "--port", "8000"]
