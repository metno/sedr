# syntax=docker/dockerfile:1

FROM ubuntu:24.04

ARG UID=1001
ARG GID=1001

# Create user with home dir
RUN groupadd --gid $GID sedr && \
  useradd \
  --create-home \
  --uid $UID \
  --gid sedr \
  sedr

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

USER sedr

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy
# uv will skip updating the environment
ENV UV_NO_SYNC=1

# Set workdir
WORKDIR /app

COPY pyproject.toml pytest.ini ./
COPY sedr/ ./sedr/

# Install dependencies, using cache from host
RUN --mount=type=cache,target=/root/.cache/uv uv sync

ENTRYPOINT ["uv", "run", "sedr"]
