# syntax=docker/dockerfile:1

# Based on https://github.com/GoogleContainerTools/distroless/blob/main/examples/python3-requirements/Dockerfile

FROM debian:12-slim AS build
RUN apt-get update && \
    apt-get install --no-install-suggests --no-install-recommends --yes python3-venv gcc libpython3-dev && \
    python3 -m venv /venv && \
    /venv/bin/pip install --upgrade pip
    # setuptools
    # wheel

# Build the virtualenv as a separate step: Only re-execute this step when requirements.txt changes
FROM build AS build-venv
COPY requirements.txt /requirements.txt
RUN /venv/bin/pip install --disable-pip-version-check -r /requirements.txt

FROM gcr.io/distroless/python3-debian12

ARG UID=65532
ARG GID=65534

COPY --from=build-venv /venv /venv

# Set workdir
WORKDIR /app

COPY pytest.ini ./
COPY sedr/ ./sedr/

# Run as nonroot user
# RUN ["mkdir", ".hypothesis", ".pytest_cache"]
# RUN ["chown", "-R", "$UID:$GID", ".hypothesis", ".pytest_cache"]
USER nonroot

ENTRYPOINT ["/venv/bin/python", "/app/sedr/__init__.py"]
