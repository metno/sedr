#!/bin/bash

export PYTHONPATH=$(pwd)
export SCHEMATHESIS_HOOKS=sedr.tests.hooks
st run --experimental=openapi-3.1 https://edrisobaric.k8s.met.no/api
