#!/bin/bash
set -vex
THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/" >/dev/null 2>&1 && pwd)"

pushd "$THIS_DIR" > /dev/null
if [ ! -d ".env" ]; then
    python3 -m venv .env
fi

source .env/bin/activate

# This won't be needed until we check more than formatting
pip install -r requirements.txt
pip install -r requirements-dev.txt

# check code formatting
black . --check

# check linting issues
pylint eclipse_opcua

# run unit tests
pytest tests --doctest-modules \
  --junitxml=junit/test-results.xml \
  --cov=eclipse_opcua \
  --cov-report=xml \
  --cov-fail-under=65

# create docker container image
CONTAINER_IMAGE_NAME=${CONTAINER_IMAGE_NAME:-'ihubmain.azurecr.io/edge/eclipse-opcua-test-harness:latest'}
docker build -t $CONTAINER_IMAGE_NAME .

popd > /dev/null
