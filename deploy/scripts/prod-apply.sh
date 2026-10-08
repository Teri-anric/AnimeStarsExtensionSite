#!/usr/bin/env bash
set -euo pipefail
set +x

script_dir="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
plan_file="${ANIMESTARS_TF_PLAN_FILE:-${TMPDIR:-/tmp}/animestars-extensionsite-prod.tfplan}"
[[ -f "$plan_file" ]] || { echo "No saved plan exists. Run task prod:tf:plan and review the actions first." >&2; exit 2; }
"${script_dir}/terraform.sh" apply -input=false "$plan_file"
rm -f -- "$plan_file"
