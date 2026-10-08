#!/usr/bin/env bash
set -euo pipefail
set +x

script_dir="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
plan_file="${ANIMESTARS_TF_PLAN_FILE:-${TMPDIR:-/tmp}/animestars-extensionsite-prod.tfplan}"
umask 077
mkdir -p "$(dirname "$plan_file")"
"${script_dir}/terraform.sh" plan -input=false -out="$plan_file"
"${script_dir}/terraform.sh" show "$plan_file"
echo "Saved private plan: $plan_file"
