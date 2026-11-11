#!/usr/bin/env bash
# Removes the lock first, then the policies, the budget and the resource group. Run with: ./teardown.sh
set -u
cd "$(dirname "$0")"
az account show >/dev/null 2>&1 || { echo "Not logged in to Azure (az login)." >&2; exit 1; }
RG=rg-guardrails
SUB=$(az account show --query id -o tsv)
if az group exists -n $RG | grep -q true; then
  for l in $(az lock list -g $RG --query '[].id' -o tsv); do az lock delete --ids "$l" && echo "removed a lock"; done
  for a in $(az policy assignment list -g $RG --query "[?starts_with(name,'guard-')].name" -o tsv); do az policy assignment delete -n "$a" -g $RG && echo "removed policy assignment $a"; done
  az rest --method delete --url "/subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.Consumption/budgets/guard-budget?api-version=2023-05-01" >/dev/null 2>&1 && echo "removed the budget"
  az group delete -n $RG --yes && echo "deleted the resource group"
fi
echo "Now run ./verify-teardown.sh"
