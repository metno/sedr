# SEDR - An OGC EDR validator

![Logo](/img/sedr.png "Logo")

## What is sedr?

An experimental validator for OGC EDR APIs. Main focus will be on the Rodeo Profile, which is a subset of the OGC EDR API.

## Who is responsible?

Team Punkt at met.no

## Status

Experiment - Every error reported might as well be an error in the validator, rather than the API.

## Getting started

### Test it out

Run docker image:

- `docker run -it --rm ghcr.io/metno/sedr --url https://edrisobaric.k8s.met.no`

Or when your service is running on localhost:

- `docker run -it --rm --network=host ghcr.io/metno/sedr --url http://localhost:8080`

Debug logging will show every request and it's status:

- Run container, mounting the current directory at /logs, and tell container to output log there: `docker run -it --rm -v .:/logs ghcr.io/metno/sedr --openapi https://edrisobaric.k8s.met.no/api --url https://edrisobaric.k8s.met.no --log-file /logs/debug.log`

### Use it for production

Run manually as noted in [Test it out](#test-it-out), or add it to your CI using one of these examples:

- [Tox](https://github.com/metno/edrisobaric/blob/main/tox.ini)
- [Github actions running tox](https://github.com/metno/edrisobaric/blob/main/.github/workflows/tests.yml)
- [Gitlab CI](https://github.com/metno/edrisobaric/blob/main/.gitlab-ci.yml)

## Overview of architecture

- __init__ includes tests from ogcapi, edrreq and rodeoprofile at startup. Tests are categorized as landing, conformance and collection.
- Landing and conformance tests are run first, in the preflight phase.
- Then schemathesis will validate the OpenAPI spec and run lots of automatic tests, including fuzzing of query parameters. Collection tests are run during this phase.

## Documentation

- Use --rodeo-profile-core to force a test against the profile core conformance class
- Use --rodeo-profile-insitu-observations to force a test against the profile insitu observations conformance class.
- Use --strict to also fail on SHOULD requirements.
- Use --log-file debug.log to get all output. For docker variant, see [Test it out](#test-it-out).

### Limitations

- Assuming Openapi 3.1
- Assuming OGC EDR API version 1.2 (draft)
- Few, basic tests for now
- Will focus more on profiles (limitations within the EDR spec) like <https://github.com/EURODEO/rodeo-edr-profile> than the full EDR spec.

### Testing the sedr code to look for regressions

For development, source a venv and run `tox p` to run all tests.

### Understanding errors from schemathesis

For each "FAILED" line, you can scroll back to see the full error and, if relevant, with a curl-example to reproduce it.

#### Wrong path to API

```bash
================================ short test summary info =================================
ERROR sedr/schemat.py::test_landingpage - Failed: Test function sedr/schemat.py::test_landingpage does not match any API operat...
ERROR sedr/schemat.py::test_conformance - Failed: Test function sedr/schemat.py::test_conformance does not match any API operat...
!!!!!!!!!!!!!!!!!!!!!!!! Interrupted: 2 errors during collection !!!!!!!!!!!!!!!!!!!!!!!!!
=================================== 2 errors in 3.51s ====================================
```

#### Wrong path to OpenAPI spec

```bash
================================ short test summary info =================================
ERROR sedr/schemat.py - schemathesis.exceptions.SchemaError: Failed to load schema due to client error (HTTP ...
!!!!!!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!!!!!!
==================================== 1 error in 2.94s ====================================
```

#### Wrong URL / port

```bash
FAILED sedr/schemat.py::test_api[GET /] - requests.exceptions.ConnectionError: HTTPConnectionPool(host='example.com', port=80): M...
```

```bash
================================ short test summary info =================================
ERROR sedr/schemat.py - schemathesis.exceptions.SchemaError: Connection failed
!!!!!!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!!!!!!
==================================== 1 error in 3.52s ====================================
```

```bash
E   schemathesis.exceptions.SchemaError: Failed to load schema due to client error (HTTP 404 Not Found)
================================ short test summary info =================================
ERROR sedr/schemat.py - schemathesis.exceptions.SchemaError: Failed to load schema due to client error (HTTP ...
!!!!!!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!!!!!!
==================================== 1 error in 3.64s ====================================
```

#### Wrong API version / missing conformance link

Sedr wants EDR 1.1, but the API is EDR 1.0.

```python
        if not requirementA2_2_A5:
>           raise AssertionError(requirementA2_2_A5_message)
E           AssertionError: Conformance page /conformance does not contain the core edr class http://www.opengis.net/spec/ogcapi-edr-1/1.1/conf/core. See <https://docs.ogc.org/is/19-086r6/19-086r6.html#_c9401fee-54b9-d116-8365-af0f85a8243d> for more info.

sedr/schemat.py:123: AssertionError

========================================= PASSES =========================================
____________________________________ test_api[GET /] _____________________________________
_______________________________ test_api[GET /conformance] _______________________________
_______________________________ test_api[GET /collections] _______________________________
________________________ test_api[GET /collections/observations] _________________________
___________________ test_api[GET /collections/observations/locations] ____________________
____________ test_api[GET /collections/observations/locations/{location_id}] _____________
____________________ test_api[GET /collections/observations/position] ____________________
______________________ test_api[GET /collections/observations/area] ______________________
_____________________ test_api[GET /collections/observations/items] ______________________
________________ test_api[GET /collections/observations/items/{item_id}] _________________
________________________________ test_landingpage[GET /] _________________________________
___________________________ test_collections[GET /collections] ___________________________
================================ short test summary info =================================
PASSED sedr/schemat.py::test_api[GET /]
PASSED sedr/schemat.py::test_api[GET /conformance]
PASSED sedr/schemat.py::test_api[GET /collections]
PASSED sedr/schemat.py::test_api[GET /collections/observations]
PASSED sedr/schemat.py::test_api[GET /collections/observations/locations]
PASSED sedr/schemat.py::test_api[GET /collections/observations/locations/{location_id}]
PASSED sedr/schemat.py::test_api[GET /collections/observations/position]
PASSED sedr/schemat.py::test_api[GET /collections/observations/area]
PASSED sedr/schemat.py::test_api[GET /collections/observations/items]
PASSED sedr/schemat.py::test_api[GET /collections/observations/items/{item_id}]
PASSED sedr/schemat.py::test_landingpage[GET /]
PASSED sedr/schemat.py::test_collections[GET /]
PASSED sedr/schemat.py::test_collections[GET /conformance]
PASSED sedr/schemat.py::test_collections[GET /collections]
PASSED sedr/schemat.py::test_collections[GET /collections/observations]
PASSED sedr/schemat.py::test_collections[GET /collections/observations/locations]
PASSED sedr/schemat.py::test_collections[GET /collections/observations/locations/{location_id}]
PASSED sedr/schemat.py::test_collections[GET /collections/observations/position]
PASSED sedr/schemat.py::test_collections[GET /collections/observations/area]
PASSED sedr/schemat.py::test_collections[GET /collections/observations/items]
PASSED sedr/schemat.py::test_collections[GET /collections/observations/items/{item_id}]
FAILED sedr/schemat.py::test_conformance[GET /conformance] - AssertionError: Conformance page /conformance does not contain the core edr class htt...
======================== 1 failed, 21 passed in 95.89s (0:01:35) =========================
```

### Components

Main components of the validator are:

- [Schemathesis](https://schemathesis.readthedocs.io/en/stable/)
- [hypothesis](https://hypothesis.readthedocs.io/en/latest/)
- [pytest](https://docs.pytest.org/en/stable/)

## How to contribute

Create an issue or start a discussion. Please do not contriute without
discussing it first.
