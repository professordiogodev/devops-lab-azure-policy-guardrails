#!/usr/bin/env bash
# Reads your guardrails and then tries to break through them. Run with: ./verify.sh
cd "$(dirname "$0")" || exit 1
az account show >/dev/null 2>&1 || { echo "Not logged in to Azure (az login)." >&2; exit 1; }
exec python3 .lab/guardcheck.py
