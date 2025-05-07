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
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set workdir
WORKDIR /app

COPY pyproject.toml pytest.ini ./
COPY sedr/ ./sedr/

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv uv tool install tox --with tox-uv; uv sync
RUN chmod a+rX -R /root

# Prepare to run as nonroot user
RUN mkdir .hypothesis .pytest_cache && \
  chown -R sedr .hypothesis .pytest_cache

USER sedr

ENTRYPOINT ["/app/.venv/bin/python", "./sedr/__init__.py"]
