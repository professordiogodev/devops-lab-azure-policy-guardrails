#!/usr/bin/env python3
import json, os, re, subprocess, sys, time
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(ROOT)
RG, LAB = "rg-guardrails", "azure-policy-guardrails"
passed = failed = 0
DEF_TAG, DEF_LOC, DEF_SKU = "871b6d14-10aa-478d-b590-94f262ecfa99", "e56962a6-4747-49cd-b67b-bf8b01975c4c", "cccc23c7-8427-4f53-ad12-b6a63eb452b3"


def check(desc, ok, hint=""):
    global passed, failed
    if ok:
        passed += 1; print("PASS  " + desc, flush=True)
    else:
        failed += 1; print("FAIL  " + desc + (("   -> " + hint) if hint else ""), flush=True)


def finish():
    print()
    print(("ALL CHECKS PASSED (%d/%d)" % (passed, passed)) if failed == 0 else ("%d check(s) failed, %d passed" % (failed, passed)))
    sys.exit(1 if failed else 0)


def az(*a, timeout=300):
    r = subprocess.run(("az",) + a, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout, r.stderr


def azj(*a):
    rc, out, err = az(*a, "-o", "json")
    try:
        return json.loads(out) if rc == 0 and out.strip() else None
    except Exception:
        return None


sub = azj("account", "show") or {}
sid = sub.get("id", "")
print("Subscription %s" % sub.get("name"))
print("== The resource group ==")
rg = azj("group", "show", "-n", RG)
check("resource group %s exists in eastus, tagged lab=%s" % (RG, LAB), bool(rg) and rg.get("location") == "eastus" and (rg.get("tags") or {}).get("lab") == LAB, "az group create -n %s -l eastus --tags lab=%s" % (RG, LAB))
if not rg:
    finish()

print("== The policies ==")
asg = azj("policy", "assignment", "list", "-g", RG) or []
asg = [a for a in asg if a["name"].startswith("guard-") and RG.lower() in a["scope"].lower()]
byd = {a["policyDefinitionId"].split("/")[-1]: a for a in asg}
check("three assignments named guard-..., scoped to the resource group (not the subscription)", len(asg) == 3 and set(byd) == {DEF_TAG, DEF_LOC, DEF_SKU}, "found: %s" % [a["name"] for a in asg])
tag = byd.get(DEF_TAG, {})
check("'Require a tag on resources' with tagName owner", (tag.get("parameters") or {}).get("tagName", {}).get("value") == "owner")
loc = byd.get(DEF_LOC, {})
locs = [x.lower() for x in (loc.get("parameters") or {}).get("listOfAllowedLocations", {}).get("value", [])]
check("'Allowed locations' allows eastus and nothing else", locs == ["eastus"], str(locs))
sku = byd.get(DEF_SKU, {})
skus = (sku.get("parameters") or {}).get("listOfAllowedSKUs", {}).get("value", [])
check("'Allowed VM SKUs' lists 1 to 6 small sizes only (B-series or 2-vCPU D)", 1 <= len(skus) <= 6 and all(re.match(r"Standard_(B|D2|DS1|A[1-2])", s) for s in skus), str(skus))
check("all three are enforced (enforcementMode Default, effect deny)", all(a.get("enforcementMode") == "Default" for a in asg) and all((a.get("parameters") or {}).get("effect", {"value": "Deny"}).get("value", "Deny") == "Deny" for a in asg))
check("every assignment has a display name or description a colleague can read", all((a.get("displayName") or a.get("description") or "").strip() for a in asg))

print("== The budget ==")
rc, out, err = az("rest", "--method", "get", "--url", "/subscriptions/%s/resourceGroups/%s/providers/Microsoft.Consumption/budgets?api-version=2023-05-01" % (sid, RG))
budgets = []
try:
    budgets = json.loads(out).get("value", []) if rc == 0 else []
except Exception:
    pass
b = next((x for x in budgets if x["name"] == "guard-budget"), None)
check("a budget named guard-budget exists on the resource group", bool(b), "Cost Management > Budgets, scope = the resource group")
if b:
    p = b["properties"]
    th = sorted(n["threshold"] for n in (p.get("notifications") or {}).values())
    check("monthly budget of 1 to 100 US dollars (the amount is %s)" % p.get("amount"), p.get("timeGrain") == "Monthly" and 1 <= float(p.get("amount", 0)) <= 100)
    check("notifications at 80%% and 100%% with at least one contact e-mail (thresholds: %s)" % th, 80 in th and 100 in th and all((n.get("contactEmails") or []) for n in p["notifications"].values()))

print("== The lock ==")
locks = azj("lock", "list", "-g", RG) or []
check("a CanNotDelete lock on the resource group", any(l.get("level") == "CanNotDelete" for l in locks))

print("== Try to break through (policies can take 5 to 15 minutes to start denying) ==")
suffix = sid.replace("-", "")[:8]
acct = "stguardtest" + suffix
base = ["storage", "account", "create", "-g", RG, "--sku", "Standard_LRS", "--kind", "StorageV2", "--min-tls-version", "TLS1_2", "--allow-blob-public-access", "false", "--allow-shared-key-access", "false"]


def attempt(name, location, tags):
    args = base + ["-n", name, "-l", location]
    if tags:
        args += ["--tags"] + tags
    return az(*args)


def denied_by_policy(name, location, tags, secs=900):
    end = time.time() + secs
    last = ""
    while time.time() < end:
        rc, out, err = attempt(name, location, tags)
        last = err
        if rc != 0 and "RequestDisallowedByPolicy" in err:
            return True, err
        if rc == 0:
            az("storage", "account", "delete", "-g", RG, "-n", name, "--yes")  # not blocked yet: undo and wait
        time.sleep(30)
    return False, last


ok, err = denied_by_policy("stguardnotag" + suffix, "eastus", None)
check("a storage account WITHOUT the owner tag is denied (RequestDisallowedByPolicy)", ok, err[-250:])
ok, err = denied_by_policy("stguardwest" + suffix, "westeurope", ["owner=checker", "lab=" + LAB], 300)
check("a storage account in westeurope is denied by the allowed-locations policy", ok, err[-250:])
rc, out, err = attempt(acct, "eastus", ["owner=checker", "lab=" + LAB])
check("a storage account in eastus WITH the owner tag is allowed", rc == 0 or "already" in err.lower(), err[-250:])
rc, out, err = az("storage", "account", "delete", "-g", RG, "-n", acct, "--yes")
check("deleting it is refused by the lock (ScopeLocked)", rc != 0 and "ScopeLocked" in err, err[-250:])
finish()
