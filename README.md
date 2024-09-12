# SEDR - An OGC EDR validator

An experiment to validate OGC EDR APIs using schemathesis, and give good feedback to developers.

## Who is responsible?

Team Punkt at met.no

## Status

Experiment

## Getting started

### Test it out

Run docker image:

- `docker run -it --rm ghcr.io/metno/sedr:main --openapi https://edrisobaric.k8s.met.no/api --url https://edrisobaric.k8s.met.no`

Debug logging will show every request and it's status:

- Create a directory: `mkdir ./logs`
- Run container, mounting the new directory at /logs, and tell container to output log there: `docker run -it --rm -v ./logs:/logs docker.io/library/sedr --openapi https://edrisobaric.k8s.met.no/api --url https://edrisobaric.k8s.met.no --log-file /logs/debug.log 

### Results testing existing services

- [edrisobaric](https://edrisobaric.k8s.met.no) works
  - <span style="color:green">......................</span>
- [FMI](https://opendata.fmi.fi/edr/) some tests works, some fails
  - <span style="color:green">.</span><span style="color:red">F</span><span style="color:green">...</span><span style="color:red">FF<span style="color:green">.</span><span style="color:red">FFFFFFFFFFFFFFFFFFFFFFFFFFFFFF<span style="color:green">.</span><span style="color:red">FFF<span style="color:green">......</span><span style="color:red">FF<span style="color:green">.........................................</span>F<span style="color:green">...............F<span style="color:green">................................................</span>
- [UK metoffice](https://labs.metoffice.gov.uk/edr)
  - fails due to /{service_id}/collections, /{service_id}/conformance?

### Use it for production

Not production ready.

## Overview of architecture

## Documentation

Schemathesis and pytest are the main components. Stateful tests are not used, as they require openapi links in the spec.

## How to contribute

Create an issue or start a discussion.

## Documentation Template

This document is based on the [Met-norway-readme](https://gitlab.met.no/maler/met-norway-readme)-template.
