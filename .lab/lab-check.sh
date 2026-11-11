#!/usr/bin/env bash
rc=0
test -s notes.md && echo "- ✅ notes.md exists" || echo "- ℹ️ notes.md is optional"
grep -qE '^ALL CHECKS PASSED \(' SUBMISSION.md && echo "- ✅ SUBMISSION.md shows ALL CHECKS PASSED" || { echo "- ❌ paste the verify.sh output ('ALL CHECKS PASSED') into SUBMISSION.md"; rc=1; }
exit $rc
