# syntax=docker/dockerfile:1

FROM ubuntu:24.04 AS runtime

# ARG UID=1001
# ARG GID=1001

# # Create user with home dir
# RUN groupadd --gid $GID sedr && \
#   useradd \
#   --create-home \
#   --shell /bin/false \
#   --uid $UID \
#   --gid sedr \
#   sedr

# Install python
RUN apt-get update && \
    apt-get install -y --no-install-recommends python3-dev \
    python3-venv && \
        apt-get clean && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

COPY *.py requirements.txt pytest.ini ./
RUN python3 -m venv ./venv && \
  ./venv/bin/pip install -r /app/requirements.txt

# # Run as nonroot user
# USER sedr

ENTRYPOINT ["/app/venv/bin/python", "sedr.py"]
