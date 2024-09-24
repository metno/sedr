# SEDR - An OGC EDR validator

An experimental validator for OGC EDR APIs using schemathesis.

## Who is responsible?

Team Punkt at met.no

## Status

Experiment

## Getting started

### Test it out

Run docker image:

- `docker run -it --rm ghcr.io/metno/sedr --openapi https://edrisobaric.k8s.met.no/api --url https://edrisobaric.k8s.met.no`

Debug logging will show every request and it's status:

- Run container, mounting the current directory at /logs, and tell container to output log there: `docker run -it --rm -v .:/logs ghcr.io/metno/sedr --openapi https://edrisobaric.k8s.met.no/api --url https://edrisobaric.k8s.met.no --log-file /logs/debug.log`

### Results testing existing services

- [edrisobaric](https://edrisobaric.k8s.met.no) works
  - <span style="color:green">......................</span>
- [FMI](https://opendata.fmi.fi/edr/) some tests works, some fails
  - <span style="color:green">.</span><span style="color:red">F</span><span style="color:green">...</span><span style="color:red">FF<span style="color:green">.</span><span style="color:red">FFFFFFFFFFFFFFFFFFFFFFFFFFFFFF<span style="color:green">.</span><span style="color:red">FFF<span style="color:green">......</span><span style="color:red">FF<span style="color:green">.........................................</span>F<span style="color:green">...............F<span style="color:green">................................................</span>
- [UK metoffice](https://labs.metoffice.gov.uk/edr)
  - fails due to /{service_id}/collections, /{service_id}/conformance?
- [E-soh](https://esoh.met.no/)
    <https://api.esoh.met.no/>

### Use it for production

Run manually as noted in [Test it out](#test-it-out), or add it to your CI using one of these examples:

- [Tox](https://github.com/metno/edrisobaric/blob/main/tox.ini)
- [Github actions running tox](https://github.com/metno/edrisobaric/blob/main/.github/workflows/tests.yml)
- [Gitlab CI](https://github.com/metno/edrisobaric/blob/main/.gitlab-ci.yml)

## Overview of architecture

## Documentation

### How to read results

A typical result looks like this:

```bash
...
PASSED sedr/schemat.py::test_locations[GET /collections/observations/position]
PASSED sedr/schemat.py::test_locations[GET /collections/observations/area]
PASSED sedr/schemat.py::test_locations[GET /collections/observations/items]
PASSED sedr/schemat.py::test_locations[GET /collections/observations/items/{item_id}]
FAILED sedr/schemat.py::test_api[GET /collections/observations/locations] - ExceptionGroup: Hypothesis found 5 distinct failures in explicit examples. (5 sub-exceptions)
FAILED sedr/schemat.py::test_api[GET /collections/observations/locations/{location_id}] - ExceptionGroup: Hypothesis found 5 distinct failures in explicit examples. (5 sub-exceptions)
FAILED sedr/schemat.py::test_api[GET /collections/observations/position] - ExceptionGroup: Hypothesis found 5 distinct failures in explicit examples. (5 sub-exceptions)
FAILED sedr/schemat.py::test_api[GET /collections/observations/area] - ExceptionGroup: Hypothesis found 5 distinct failures in explicit examples. (5 sub-exceptions)
FAILED sedr/schemat.py::test_api[GET /collections/observations/items] - ExceptionGroup: Hypothesis found 5 distinct failures in explicit examples. (5 sub-exceptions)
FAILED sedr/schemat.py::test_api[GET /collections/observations/items/{item_id}] - AssertionError: Request to https://api.esoh.met.no/collections/observations/items/0 failed: Custom check failed...
FAILED sedr/schemat.py::test_positions[GET /collections/observations/position] - ExceptionGroup: Hypothesis found 5 distinct failures in explicit examples. (5 sub-exceptions)
FAILED sedr/schemat.py::test_locations[GET /collections/observations/locations] - ExceptionGroup: Hypothesis found 5 distinct failures in explicit examples. (5 sub-exceptions)
========================================== 8 failed, 34 passed in 49.41s ===========================================
```

For each "FAILED" line, you can scroll back to see the full error and, if relevant, with a curl-example to reproduce it.

```python
    |     assert "name" in json.loads(
    |            ^^^^^^^^^^^^^^^^^^^^^
    | AssertionError: Expected "name": "locations" in /locations, didn't find "name".
    | Falsifying explicit example: test_locations(
    |     case=Case(query={'bbox': '5.0,52.0,6.0,52.1', 'datetime': '2022-01-01T00:00Z', 'parameter-name': 'wind_from_direction:2.0:mean:PT10M,wind_speed:10:mean:PT10M,relative_humidity:2.0:mean:PT1M,air_pressure_at_sea_level:1:mean:PT1M,air_temperature:1.5:maximum:PT10M', 'standard_names': 'wind_from_direction,wind_speed,relative_humidity,air_pressure_at_sea_level,air_temperature', 'levels': '../10.0', 'methods': 'mean, maximum, minimum', 'periods': ''}),
    | )
```

Here you can see that the test failed due to missing a "name" field in the response.

### Components

Main components of the validator are:

- [Schemathesis](https://schemathesis.readthedocs.io/en/stable/)
- [hypothesis}](https://hypothesis.readthedocs.io/en/latest/)
- [pytest](https://docs.pytest.org/en/stable/)

### Limitations

- Assuming Openapi 3.1
- Assuming OGC EDR API version 1.1
- Basic tests for now
- Profiles are not yet supported

## How to contribute

Create an issue or start a discussion. Please do not contriute without discussing it first.

## Documentation Template

This document is based on the [Met-norway-readme](https://gitlab.met.no/maler/met-norway-readme)-template.
