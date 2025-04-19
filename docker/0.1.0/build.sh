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
  # List possible pip config files.
  config_files=( "$HOME/.config/pip/pip.conf" /etc/pip/pip.conf )

  # Search for a pip config file that contains extra-index-url.
  for file in "${config_files[@]}"; do
    if [ -f "$file" ]; then
      # Find the first occurence (case-insensitive) of extra-index-url.
      line=$(grep -i "extra-index-url" "$file" | head -n 1)

      if [ -n "$line" ]; then
        # Extract the value after '=' and trim spaces.
        urls=$(echo "$line" | cut -d'=' -f2 | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

        if [ -n "$urls" ]; then
          first_url=$(echo "$urls" | awk '{print $1}')
          export EXTRA_INDEX_URL="$first_url"
          echo "Found EXTRA_INDEX_URL: $EXTRA_INDEX_URL"
          break
        fi
      fi
    fi
  done
fi

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

exit $result
