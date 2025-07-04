# Changelog

## [v0.16.0](https://github.com/metno/sedr/releases/tag/v0.16.0) (2025-06-24)

- Rename profile. Arguments now look like this:

```bash
--metocean-profile-core
                        Use the metocean profile core conformance class even though the API doesn't specify it. Default False.
--metocean-profile-insitu-observations
                        Use the metocean profile core conformance class even though the API doesn't specify it. Default False.
```

## [v0.15.0](https://github.com/metno/sedr/releases/tag/v0.15.0) (2025-06-04)

- Bug fix: Correct how CoverageJSON `coverages` and `parameters` are parsed.
- Enhancement: Increase geographical area to use for area data queries inside extent, to improve chance of getting data back.

## [v0.14.1](https://github.com/metno/sedr/releases/tag/v0.14.1) (2025-05-30)

## [v0.14.0](https://github.com/metno/sedr/releases/tag/v0.14.0) (2025-05-30)

- Started using changelog
- **Breaking change**: --rodeo-profile-core is now False by default. To enable rodeo-profile tests you should add the argument --rodeo-profile-core or add the Rodeo Profile URL to your conformance classes.

### Example

    > curl https://edrisobaric.k8s.met.no/conformance
    {
      "conformsTo": [
        "http://www.opengis.net/spec/ogcapi-common-1/1.0/conf/core",
        "http://www.opengis.net/spec/ogcapi-common-2/1.0/conf/collections",
        "http://www.opengis.net/spec/ogcapi-edr-1/1.1/conf/core",
        "http://www.opengis.net/spec/ogcapi-edr-1/1.2/req/oas31",
        "http://www.opengis.net/spec/ogcapi-edr-1/1.0/conf/covjson",
        "http://www.opengis.net/spec/ogcapi-edr-1/1.0/conf/queries",
        "http://rodeo-project.eu/spec/rodeo-edr-profile/1/req/core"
      ]
    }
