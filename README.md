# SEDR - An OGC EDR validator

An experiment to validate OGC EDR APIs using schemathesis.

## Who is responsible?

Team Punkt at met.no

## Status

Experiment

## Getting started

### Test it out

Run docker image:

- `docker run -it --rm docker.io/library/sedr --openapi https://edrisobaric.k8s.met.no/api --url https://edrisobaric.k8s.met.no`

Debug logging:

- Create a directory: `mkdir ./logs`
- Run container, mounting the new directory at /logs, and tell container to output log there: `docker run -it --rm -v ./logs:/logs docker.io/library/sedr --openapi https://edrisobaric.k8s.met.no/api --url https://edrisobaric.k8s.met.no --log-file /logs/debug.log 

### Results testing existing services

- [edrisobaric](https://edrisobaric.k8s.met.no) works
  - ......................
- [FMI](https://opendata.fmi.fi/edr/) some tests works, some fails
  - .F...FF.FFFFFFFFFFFFFFFFFFFFFFFFFFFFFF.FFF......FF.........................................F...............F................................................
- [UK metoffice](https://labs.metoffice.gov.uk/edr)
  - fails due to /{service_id}/collections, /{service_id}/conformance?

### Use it for production

## Overview of architecture

## Documentation

## How to contribute

## Documentation Template

This document is based on the [Met-norway-readme](https://gitlab.met.no/maler/met-norway-readme)-template.
