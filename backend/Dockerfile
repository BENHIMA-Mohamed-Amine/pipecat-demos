FROM python:3.12-slim

# System deps for aiortc (webrtc) and PyAV (audio processing)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsrtp2-1 \
    libopus0 \
    libvpx9 \
    && rm -rf /var/lib/apt/lists/*

# Pin uv version for reproducible builds
COPY --from=ghcr.io/astral-sh/uv:0.6.9 /uv /uvx /usr/local/bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Install dependencies only (cached layer — not invalidated by app code changes)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-dev --no-install-project

# Copy application code and data
COPY app/ ./app/
COPY data/ ./data/

# Install the project itself
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-dev

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3000"]
