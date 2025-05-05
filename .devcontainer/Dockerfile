# syntax=docker/dockerfile:1

FROM mcr.microsoft.com/vscode/devcontainers/python:3.12

# https://medium.com/@dexterwilliams04/getting-started-with-python-3-dev-containers-4f14821fec6b
ENV PIP_TARGET=/usr/local/pip-global
ENV PYTHONPATH=${PIP_TARGET}:${PYTHONPATH}
ENV PATH=${PIP_TARGET}/bin:${PATH}
RUN mkdir -p ${PIP_TARGET} \
    && chown vscode:root ${PIP_TARGET} \
    && echo "if [ \"\$(stat -c '%U' ${PIP_TARGET})\" != \"vscode\" ]; then chown -R vscode:root ${PIP_TARGET}; fi" \
        | tee -a /root/.bashrc /home/vscode/.bashrc /root/.zshrc >> /home/vscode/.zshrc 

# Set workdir
WORKDIR /app

COPY requirements.txt pytest.ini ./
COPY sedr/ ./sedr/
RUN python3 -m venv ./venv && \
  ./venv/bin/pip install -r /app/requirements.txt
