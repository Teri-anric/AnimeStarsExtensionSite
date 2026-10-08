#!/usr/bin/env bash
set -euo pipefail
set +x

script_dir="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=deploy/scripts/common.sh
source "${script_dir}/common.sh"
load_deploy_env

cd "$SITE_ROOT"
ssh_target="${SSH_TARGET:-${PROD_SSH_TARGET:-}}"
[[ -n "$ssh_target" ]] || { echo "Set SSH_TARGET in deploy/.env or the environment." >&2; exit 2; }
image_tag="$(resolve_image_tag)"
kubeconfig_path="$(resolve_kubeconfig)"
kube_context="$(resolve_kube_context)"
require_s0_ready "$kubeconfig_path" "$kube_context"

registry_namespace="${REGISTRY_NAMESPACE:-sanberry-registry}"
registry_service="${REGISTRY_SERVICE:-registry}"
registry_host="$(kubectl --kubeconfig "$kubeconfig_path" --context "$kube_context" \
  -n "$registry_namespace" get service "$registry_service" -o jsonpath='{.spec.clusterIP}')"
[[ -n "$registry_host" && "$registry_host" != "None" ]] || { echo "The existing registry Service has no ClusterIP." >&2; exit 1; }

local_port="${REGISTRY_LOCAL_PORT:-5000}"
remote_port="${REGISTRY_REMOTE_PORT:-5000}"
backend_image="${BACKEND_IMAGE:-localhost:5000/animestars-extensionsite-backend}"
frontend_image="${FRONTEND_IMAGE:-localhost:5000/animestars-extensionsite-frontend}"
api_url="${VITE_API_URL:-https://ass-api.strawberrycat.dev}"
for image in "$backend_image" "$frontend_image"; do
  [[ "$image" =~ ^[A-Za-z0-9._:/-]+$ ]] || { echo "Invalid image repository override." >&2; exit 2; }
done

ssh -o ExitOnForwardFailure=yes -N \
  -L "127.0.0.1:${local_port}:${registry_host}:${remote_port}" "$ssh_target" &
tunnel_pid=$!
cleanup() {
  kill "$tunnel_pid" 2>/dev/null || true
  wait "$tunnel_pid" 2>/dev/null || true
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

ready=0
for _ in $(seq 1 40); do
  if curl -fsS --max-time 1 "http://127.0.0.1:${local_port}/v2/" >/dev/null 2>&1; then
    ready=1
    break
  fi
  sleep 0.25
done
[[ "$ready" == 1 ]] || { echo "The existing registry did not become reachable through the SSH forward." >&2; exit 1; }

backend_path="${backend_image#*/}"
frontend_path="${frontend_image#*/}"
for image_path in "$backend_path" "$frontend_path"; do
  status="$(curl -sS --max-time 5 -o /dev/null -w '%{http_code}' \
    -H 'Accept: application/vnd.oci.image.index.v1+json, application/vnd.oci.image.manifest.v1+json, application/vnd.docker.distribution.manifest.list.v2+json, application/vnd.docker.distribution.manifest.v2+json' \
    "http://127.0.0.1:${local_port}/v2/${image_path}/manifests/${image_tag}")"
  if [[ "$status" == "200" ]]; then
    echo "Refusing to overwrite existing image tag ${image_path}:${image_tag}. Choose a new IMAGE_TAG." >&2
    exit 2
  elif [[ "$status" != "404" ]]; then
    echo "Could not verify that image tag ${image_path}:${image_tag} is unused (registry returned HTTP ${status})." >&2
    exit 1
  fi
done

docker build -f docker/Dockerfile -t "${backend_image}:${image_tag}" .
docker tag "${backend_image}:${image_tag}" "127.0.0.1:${local_port}/${backend_path}:${image_tag}"
docker push "127.0.0.1:${local_port}/${backend_path}:${image_tag}"

docker build -f docker/Dockerfile.frontend --target production --build-arg "VITE_API_URL=${api_url}" \
  -t "${frontend_image}:${image_tag}" .
docker tag "${frontend_image}:${image_tag}" "127.0.0.1:${local_port}/${frontend_path}:${image_tag}"
docker push "127.0.0.1:${local_port}/${frontend_path}:${image_tag}"

echo "Pushed backend and frontend images with tag ${image_tag}."
