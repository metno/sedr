# syntax=docker/dockerfile:1

FROM mcr.microsoft.com/vscode/devcontainers/python:3.12

# Set workdir
WORKDIR /app

# Install dependencies
COPY requirements.txt pytest.ini ./
# Copy code
COPY sedr/ ./sedr/
