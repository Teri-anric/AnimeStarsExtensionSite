#!/usr/bin/env bash
set -euo pipefail
set +x

script_dir="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=deploy/scripts/common.sh
source "${script_dir}/common.sh"
load_deploy_env

[[ "$#" -gt 0 ]] || { echo "Usage: deploy/scripts/terraform.sh <terraform arguments>" >&2; exit 2; }
kubeconfig_path="$(resolve_kubeconfig)"
kube_context="$(resolve_kube_context)"
export TF_VAR_kubeconfig_path="${TF_VAR_kubeconfig_path:-$kubeconfig_path}"
export TF_VAR_kube_context="${TF_VAR_kube_context:-$kube_context}"
exec terraform -chdir="$TERRAFORM_ROOT" "$@"
