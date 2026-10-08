#!/usr/bin/env bash
set -euo pipefail
set +x

script_dir="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=deploy/scripts/common.sh
source "${script_dir}/common.sh"
load_deploy_env

cd "$SITE_ROOT"
kubeconfig_path="$(resolve_kubeconfig)"
kube_context="$(resolve_kube_context)"
namespace="${NAMESPACE:-animestars-extension-site}"
image_tag="$(resolve_image_tag)"
require_s0_ready "$kubeconfig_path" "$kube_context"

backend_image="${BACKEND_IMAGE:-localhost:5000/animestars-extensionsite-backend}:${image_tag}"
frontend_image="${FRONTEND_IMAGE:-localhost:5000/animestars-extensionsite-frontend}:${image_tag}"
for image in "$backend_image" "$frontend_image"; do
  [[ "$image" =~ ^[A-Za-z0-9._:/-]+$ ]] || { echo "Invalid image reference." >&2; exit 2; }
done

[[ -f "${TERRAFORM_ROOT}/backend.hcl" ]] || {
  echo "${TERRAFORM_ROOT}/backend.hcl is missing; configure the remote state backend first." >&2
  exit 2
}
[[ -f "${TERRAFORM_ROOT}/terraform.tfvars" ]] || {
  echo "${TERRAFORM_ROOT}/terraform.tfvars is missing; configure runtime secrets and cluster settings first." >&2
  exit 2
}

exec 9>"${TMPDIR:-/tmp}/animestars-extensionsite-deploy.lock"
flock -n 9 || { echo "Another AnimeStarsExtensionSite rollout is in progress." >&2; exit 1; }

tag_slug="$(printf '%s' "$image_tag" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9-]+/-/g; s/^-+|-+$//g' | cut -c1-8)"
[[ -n "$tag_slug" ]] || { echo "IMAGE_TAG cannot form a Kubernetes Job name." >&2; exit 2; }

export TF_VAR_backend_image="$backend_image"
export TF_VAR_frontend_image="$frontend_image"
export TF_VAR_migration_job_name="animestars-extension-site-alembic-${tag_slug}-$(date -u +%Y%m%d%H%M%S)"

echo "Terraform will show the plan and ask before applying app-owned Kubernetes changes."
"${script_dir}/terraform.sh" apply

for workload in statefulset/postgres deployment/redis deployment/mitmproxy deployment/backend deployment/scheduler deployment/frontend; do
  kubectl --kubeconfig "$kubeconfig_path" --context "$kube_context" -n "$namespace" \
    rollout status "$workload" --timeout=10m
done

echo "AnimeStarsExtensionSite Terraform rollout completed with image tag ${image_tag}."
