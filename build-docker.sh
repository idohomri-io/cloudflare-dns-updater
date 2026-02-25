#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

docker build --platform linux/amd64 -t cfddns "$SCRIPT_DIR" --no-cache
docker tag cfddns ghcr.io/idohomri-io/cfddns:latest
docker push ghcr.io/idohomri-io/cfddns:latest