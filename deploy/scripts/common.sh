#!/usr/bin/env bash
set -euo pipefail
set +x

SITE_ROOT="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
DEPLOY_ROOT="${SITE_ROOT}/deploy"
TERRAFORM_ROOT="${DEPLOY_ROOT}/terraform"

load_deploy_env() {
  if [[ -f "${DEPLOY_ROOT}/.env" ]]; then
    set -a
    # shellcheck disable=SC1091
    source "${DEPLOY_ROOT}/.env"
    set +a
  fi
}

resolve_kubeconfig() {
  local path="${KUBECONFIG_PATH:-${PROD_KUBECONFIG:-$HOME/.kube/k3s-s1.yaml}}"
  case "$path" in
    "~/"*) path="$HOME/${path#\~/}" ;;
    "~") path="$HOME" ;;
  esac
  printf '%s\n' "$path"
}

resolve_kube_context() {
  printf '%s\n' "${KUBE_CONTEXT:-${PROD_CONTEXT:-k3s}}"
}

resolve_image_tag() {
  local tag="${IMAGE_TAG:-}"
  if [[ -z "$tag" ]]; then
    tag="$(git -C "$SITE_ROOT" rev-parse --short HEAD)"
  fi
  if [[ ! "$tag" =~ ^[A-Za-z0-9_][A-Za-z0-9_.-]{0,127}$ ]]; then
    echo "IMAGE_TAG contains unsupported characters." >&2
    return 2
  fi
  printf '%s\n' "$tag"
}

require_s0_ready() {
  local kubeconfig_path="$1"
  local kube_context="$2"
  local ready
  ready="$(kubectl --kubeconfig "$kubeconfig_path" --context "$kube_context" get node s0.teri -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}')"
  [[ "$ready" == "True" ]] || { echo "K3s node s0.teri is not Ready in the selected context." >&2; return 1; }
}
