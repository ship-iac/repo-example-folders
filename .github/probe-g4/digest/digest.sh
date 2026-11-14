#!/usr/bin/env bash
set -euo pipefail
if [ -n "$FILE" ] && [ -f "$FILE" ]; then
  echo "shipmate-state-digest=$(sha256sum "$FILE" | cut -c1-64) path=$STATE_PATH"
else
  echo "shipmate-state-digest=none"
fi
