#!/bin/bash

# export PYTHONPATH=$(pwd)
export SCHEMATHESIS_HOOKS=sedr.hooks
st run \
    --experimental=openapi-3.1 \
    --checks all \
    --workers 8 \
    --include-path-regex '/collections$' \
    --hypothesis-suppress-health-check=too_slow \
    https://edrisobaric.k8s.met.no/api
