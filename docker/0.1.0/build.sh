#!/usr/bin/env bash

set -x

proxy_settings=()

if [ -n "$http_proxy" ]; then
  proxy_settings+=("--build-arg" "http_proxy=$http_proxy")
fi

if [ -n "$https_proxy" ]; then
  proxy_settings+=("--build-arg" "https_proxy=$https_proxy")
fi

if [ -n "$ftp_proxy" ]; then
  proxy_settings+=("--build-arg" "ftp_proxy=$ftp_proxy")
fi

if [ -n "$no_proxy" ]; then
  proxy_settings+=("--build-arg" "no_proxy=$no_proxy")
fi

if [ ${#proxy_settings[@]} -gt 0 ]; then
  echo "Proxy settings were found and will be used during the build."
fi

other_settings=()

if [ -z "$EXTRA_INDEX_URL" ]; then
  echo "EXTRA_INDEX_URL is not set" >&2
  exit 1
fi

other_settings+=("--build-arg" "EXTRA_INDEX_URL=$EXTRA_INDEX_URL")

if [ -z "$EXTRA_INDEX_HOST" ]; then
  EXTRA_INDEX_HOST=$(echo "$EXTRA_INDEX_URL" | awk -F/ '{print $3}')

  if [ -z "$EXTRA_INDEX_HOST" ]; then
    echo "EXTRA_INDEX_HOST is not set" >&2
    exit 1
  fi

  other_settings+=("--build-arg" "EXTRA_INDEX_HOST=$EXTRA_INDEX_HOST")
fi

tag_name=$(basename "$(cd "$(dirname "${BASH_SOURCE[0]}")"; pwd)")
tag_name=${tag_name//[!0-9a-zA-Z.-_]/-}
docker build "${proxy_settings[@]}" "${other_settings[@]}" --no-cache=true -t ragflow-knowledge-mcp-server:"$tag_name" .
result=$?

yes | docker image prune > /dev/null

exit $result
