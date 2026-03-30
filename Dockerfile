# =============================================================================
# imdbapi-client — FastAPI application images
#
# Build context: backend/imdbapi (submodule root)
#
# Targets:
#   dev      Local Docker-only development image used by docker-compose.yml
#   runtime  Production image used by Jenkins
# =============================================================================

FROM python:3.13-slim AS uv-base

# Pin uv to a minor series for reproducible local and CI images.
COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /usr/local/bin/uv

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_LINK_MODE=copy


# ---- Stage 1: dev -----------------------------------------------------------
# Used by `docker-compose.yml` and VS Code "Attach to Running Container".
FROM uv-base AS dev

# Install development tools needed for VS Code, quality commands, and make shell.
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    zsh \
    make \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Configure a minimal shell prompt without internet downloads.
RUN printf 'export PS1="[imdbapi] %n@%m:%~%% "\nalias ls="ls --color=auto"\nalias ll="ls -alF"\n' \
    > /root/.zshrc

RUN git config --global --add safe.directory /workspace

WORKDIR /workspace

# Keep the interpreter in a stable location so VS Code launch/settings can
# point to `/opt/venv/bin/python` inside the attached container.
RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH" \
    VIRTUAL_ENV="/opt/venv" \
    PYTHONPATH="/workspace/src"

# Copy manifests only so Docker can cache the dependency layer aggressively.
# `--no-install-project` keeps the source tree out of the image because local
# development bind-mounts the live checkout into /workspace at runtime.
COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --all-groups --active --no-install-project

CMD ["sleep", "infinity"]


# ---- Stage 2: builder -------------------------------------------------------
FROM uv-base AS builder

WORKDIR /build

# Copy workspace manifests and lock file first for layer caching.
COPY pyproject.toml uv.lock ./

# Install production dependencies with robust caching.
# The runtime stage copies this venv directly.
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable --no-install-project

# Copy actual source after dependencies are cached.
COPY src ./src
COPY main.py ./


# ---- Stage 3: runtime -------------------------------------------------------
FROM python:3.13-slim AS runtime

LABEL org.opencontainers.image.title="imdbapi-client"
LABEL org.opencontainers.image.description="Async IMDb REST API client"

RUN useradd --system --uid 1001 --no-create-home appuser

WORKDIR /app

# Copy only the pre-built venv and source tree from the builder.
# `--link` creates independent layers that BuildKit can cache and resolve in
# parallel — safe to use with multi-stage copies.
COPY --link --from=builder /build/.venv /app/.venv
COPY --link --from=builder /build/src /app/src
COPY --link --from=builder /build/main.py /app/main.py

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/src"

USER appuser

CMD ["python", "main.py"]
