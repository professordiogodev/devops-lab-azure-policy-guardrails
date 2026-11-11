#!/usr/bin/env bash
# Checks your tools and your Azure login. Creates nothing in Azure. Run: ./setup.sh
set -u
cd "$(dirname "$0")"
for c in az python3; do command -v "$c" >/dev/null || { echo "MISSING: $c"; exit 1; }; done
az account show >/dev/null 2>&1 || { echo "Not logged in to Azure. Run: az login"; exit 1; }
cat <<TXT
Ready.
  Subscription:   $(az account show --query name -o tsv)
  You are:        $(az account show --query user.name -o tsv)
  Resource group: rg-guardrails  (region: eastus), tagged lab=azure-policy-guardrails
  Everything in this lab is scoped to that ONE resource group: it cannot affect the rest of the subscription.
  Names to use:   policy assignments starting with "guard-", budget "guard-budget", lock "guard-lock"
Nothing exists in Azure yet.
TXT
