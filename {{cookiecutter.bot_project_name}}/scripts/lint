#!/usr/bin/env bash

set -ex

black --check --diff app tests
isort --profile black --check-only app tests

mypy app tests
flake8 app tests
