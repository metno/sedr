# syntax=docker/dockerfile:1

# build:
# docker buildx build -t sedr -f Dockerfile .

# run:
# docker run -it --rm sedr --openapi https://edrisobaric.k8s.met.no/api --url https://edrisobaric.k8s.met.no

FROM ubuntu:24.04

# Create user with home dir
RUN useradd --create-home sedr

# Install python and libeccodes-dev. Create /data.
RUN apt-get update && \
    apt-get install -y --no-install-recommends python3-dev python3-pip \
    python3-venv && \
        apt-get clean && rm -rf /var/lib/apt/lists/*

# Set workdir and install app with requirements.
WORKDIR /app
COPY *.py requirements.txt pytest.ini ./
RUN python3 -m venv ./venv && \
  ./venv/bin/pip install -r /app/requirements.txt

# Run as nonroot user
USER sedr

ENTRYPOINT ["/app/venv/bin/python", "sedr.py"]
