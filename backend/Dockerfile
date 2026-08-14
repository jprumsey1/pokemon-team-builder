FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim
ENV UV_PROJECT_ENVIRONMENT=/opt/venv UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy \
    PATH=/opt/venv/bin:$PATH PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project     # cached layer: deps change rarely
COPY . .
RUN uv sync --locked
CMD ["fastapi", "run", "app/main.py"]
