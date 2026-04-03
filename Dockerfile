# =============================================================================
# imdbapi-client — Async IMDb REST API client
#
# Targets:
#   dev      Attached-container image used by docker-compose.yml and VS Code
#   builder  Intermediate dependency synchronization stage
#   runtime  Production image used by Jenkins
# =============================================================================

FROM python:3.13-slim AS uv-base

COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /usr/local/bin/uv

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_LINK_MODE=copy


# ---- Stage 1: dev -----------------------------------------------------------
FROM uv-base AS dev

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    make \
    && rm -rf /var/lib/apt/lists/*

RUN git config --global --add safe.directory /workspace

WORKDIR /workspace

RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH" \
    VIRTUAL_ENV="/opt/venv" \
    PYTHONPATH="/workspace/src"

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --all-groups --active --no-install-project --no-install-workspace

CMD ["sleep", "infinity"]


# ---- Stage 2: builder -------------------------------------------------------
FROM uv-base AS builder

WORKDIR /build

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable --no-install-project

COPY src src/
COPY main.py ./


# ---- Stage 3: runtime -------------------------------------------------------
FROM python:3.13-slim AS runtime

LABEL org.opencontainers.image.title="imdbapi-client"
LABEL org.opencontainers.image.source="https://github.com/aharbii/imdbapi-client"
LABEL org.opencontainers.image.description="Async IMDb REST API client"
LABEL org.opencontainers.image.licenses="MIT"

RUN useradd --system --uid 1001 --no-create-home appuser

WORKDIR /app

COPY --link --from=builder /build/.venv /app/.venv
COPY --link --from=builder /build/src ./src
COPY --link --from=builder /build/main.py ./main.py

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/src" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER appuser

CMD ["python", "main.py"]
