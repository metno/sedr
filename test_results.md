# Test results for existing services

## [edrisobaric](https://edrisobaric.k8s.met.no)

Works 100%

## [FMI](https://opendata.fmi.fi/edr/) some tests works, some fails
  - <span style="color:green">.</span><span style="color:red">F</span><span style="color:green">...</span><span style="color:red">FF<span style="color:green">.</span><span style="color:red">FFFFFFFFFFFFFFFFFFFFFFFFFFFFFF<span style="color:green">.</span><span style="color:red">FFF<span style="color:green">......</span><span style="color:red">FF<span style="color:green">.........................................</span>F<span style="color:green">...............F<span style="color:green">................................................</span>

## [UK metoffice](https://labs.metoffice.gov.uk/edr)
  - fails due to /{service_id}/collections, /{service_id}/conformance?

## [E-soh](https://esoh.met.no/)
    <https://api.esoh.met.no/>

```bash
______________________________________________ test_collections[GET /collections] ______________________________________________
=================================================== short test summary info ====================================================
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
PASSED sedr/schemat.py::test_conformance[GET /conformance]
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
PASSED sedr/schemat.py::test_positions[GET /]
PASSED sedr/schemat.py::test_positions[GET /conformance]
PASSED sedr/schemat.py::test_positions[GET /collections]
PASSED sedr/schemat.py::test_positions[GET /collections/observations]
PASSED sedr/schemat.py::test_positions[GET /collections/observations/locations]
PASSED sedr/schemat.py::test_positions[GET /collections/observations/locations/{location_id}]
PASSED sedr/schemat.py::test_positions[GET /collections/observations/area]
PASSED sedr/schemat.py::test_positions[GET /collections/observations/items]
PASSED sedr/schemat.py::test_positions[GET /collections/observations/items/{item_id}]
PASSED sedr/schemat.py::test_locations[GET /]
PASSED sedr/schemat.py::test_locations[GET /conformance]
PASSED sedr/schemat.py::test_locations[GET /collections]
PASSED sedr/schemat.py::test_locations[GET /collections/observations]
PASSED sedr/schemat.py::test_locations[GET /collections/observations/locations/{location_id}]
PASSED sedr/schemat.py::test_locations[GET /collections/observations/position]
PASSED sedr/schemat.py::test_locations[GET /collections/observations/area]
PASSED sedr/schemat.py::test_locations[GET /collections/observations/items]
PASSED sedr/schemat.py::test_locations[GET /collections/observations/items/{item_id}]
FAILED sedr/schemat.py::test_positions[GET /collections/observations/position] - ExceptionGroup: Hypothesis found 5 distinct failures in explicit examples. (5 sub-exceptions)
FAILED sedr/schemat.py::test_locations[GET /collections/observations/locations] - ExceptionGroup: Hypothesis found 5 distinct failures in explicit examples. (5 sub-exceptions)
=========================================== 2 failed, 40 passed in 194.46s (0:03:14) ===========================================
```
