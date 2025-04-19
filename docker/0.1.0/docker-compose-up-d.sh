#!/usr/bin/env bash
set -x

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

# If EXTRA_INDEX_URL is not found, exit with an error.
if [ -z "$EXTRA_INDEX_URL" ]; then
  exit 1
fi

if [ -z "$EXTRA_INDEX_HOST" ]; then
  export EXTRA_INDEX_HOST=$(echo "$EXTRA_INDEX_URL" | awk -F/ '{print $3}')
fi

if [ -z "$EXTRA_INDEX_HOST" ]; then
  echo "Failed to extract EXTRA_INDEX_HOST from EXTRA_INDEX_URL"
  exit 1
fi

echo "Final EXTRA_INDEX_HOST: $EXTRA_INDEX_HOST"

# Determine which command to use: docker-compose or docker compose.
if command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD="docker-compose"
else
  COMPOSE_CMD="docker compose"
fi

# Bring up docker containers in detached mode using the chosen command.
${COMPOSE_CMD} up -d || exit 1

echo "Docker containers are up and running."
