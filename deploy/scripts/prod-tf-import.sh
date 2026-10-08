#!/usr/bin/env bash
set -euo pipefail
set +x

script_dir="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=deploy/scripts/common.sh
source "${script_dir}/common.sh"
load_deploy_env

[[ "${IMPORT_EXISTING_RESOURCES:-}" == "true" ]] || {
  echo "Set IMPORT_EXISTING_RESOURCES=true after confirming this is the dedicated AnimeStarsExtensionSite state." >&2
  exit 2
}
[[ -f "${TERRAFORM_ROOT}/backend.hcl" ]] || {
  echo "${TERRAFORM_ROOT}/backend.hcl is missing; copy backend.hcl.example and configure backend credentials first." >&2
  exit 2
}
[[ -f "${TERRAFORM_ROOT}/terraform.tfvars" ]] || {
  echo "${TERRAFORM_ROOT}/terraform.tfvars is missing; configure runtime secrets before importing." >&2
  exit 2
}

kubeconfig_path="$(resolve_kubeconfig)"
kube_context="$(resolve_kube_context)"
require_s0_ready "$kubeconfig_path" "$kube_context"

"${script_dir}/terraform.sh" init -input=false -backend-config=backend.hcl

state_has() {
  "${script_dir}/terraform.sh" state list 2>/dev/null | grep -Fxq -- "$1"
}

import_if_exists() {
  local address="module.extensionsite_app.$1"
  local resource_type="$2"
  local name="$3"
  local namespace="$4"
  local identifier="$5"

  if state_has "$address"; then
    echo "Already in state: ${address}"
    return
  fi

  if [[ -n "$namespace" ]]; then
    if ! kubectl --kubeconfig "$kubeconfig_path" --context "$kube_context" -n "$namespace" get "$resource_type" "$name" >/dev/null 2>&1; then
      echo "Not present; Terraform will create it if still desired: ${resource_type}/${name}"
      return
    fi
  elif ! kubectl --kubeconfig "$kubeconfig_path" --context "$kube_context" get "$resource_type" "$name" >/dev/null 2>&1; then
    echo "Not present; Terraform will create it if still desired: ${resource_type}/${name}"
    return
  fi

  "${script_dir}/terraform.sh" import -input=false "$address" "$identifier"
}

namespace="animestars-extension-site"
import_if_exists kubernetes_namespace_v1.site namespace "$namespace" "" "$namespace"
import_if_exists kubernetes_persistent_volume_v1.preserved_postgres pv animestars-extension-site-postgres-s0 "" animestars-extension-site-postgres-s0
import_if_exists kubernetes_persistent_volume_claim_v1.preserved_postgres pvc postgres-data "$namespace" "$namespace/postgres-data"
import_if_exists kubernetes_persistent_volume_v1.active_postgres pv animestars-extension-site-postgres-restore-s0 "" animestars-extension-site-postgres-restore-s0
import_if_exists kubernetes_persistent_volume_claim_v1.active_postgres pvc postgres-restore-data "$namespace" "$namespace/postgres-restore-data"

import_if_exists kubernetes_secret_v1.runtime secret runtime-secrets "$namespace" "$namespace/runtime-secrets"
import_if_exists kubernetes_config_map_v1.runtime configmap runtime-config "$namespace" "$namespace/runtime-config"

import_if_exists kubernetes_service_v1.postgres service postgres "$namespace" "$namespace/postgres"
import_if_exists kubernetes_stateful_set_v1.postgres statefulset postgres "$namespace" "$namespace/postgres"
import_if_exists kubernetes_service_v1.redis service redis "$namespace" "$namespace/redis"
import_if_exists kubernetes_deployment_v1.redis deployment redis "$namespace" "$namespace/redis"
import_if_exists kubernetes_service_v1.mitmproxy service mitmproxy "$namespace" "$namespace/mitmproxy"
import_if_exists kubernetes_deployment_v1.mitmproxy deployment mitmproxy "$namespace" "$namespace/mitmproxy"
import_if_exists kubernetes_service_v1.backend service backend "$namespace" "$namespace/backend"
import_if_exists kubernetes_service_v1.frontend service frontend "$namespace" "$namespace/frontend"

migration_job_name="${TF_VAR_migration_job_name:-animestars-extension-site-alembic-upgrade}"
TF_VAR_migration_job_name="$migration_job_name" import_if_exists \
  kubernetes_job_v1.alembic job "$migration_job_name" "$namespace" "$namespace/$migration_job_name"

import_if_exists kubernetes_deployment_v1.backend deployment backend "$namespace" "$namespace/backend"
import_if_exists kubernetes_deployment_v1.frontend deployment frontend "$namespace" "$namespace/frontend"
import_if_exists kubernetes_deployment_v1.scheduler deployment scheduler "$namespace" "$namespace/scheduler"
import_if_exists kubernetes_manifest.site_ingress_route ingressroute.traefik.io animestars-extension-site "$namespace" \
  "apiVersion=traefik.io/v1alpha1,kind=IngressRoute,namespace=${namespace},name=animestars-extension-site"

echo "Import complete. Review task prod:tf:plan before applying."
