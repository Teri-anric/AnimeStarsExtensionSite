#!/usr/bin/env bash
set -euo pipefail
set +x

script_dir="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=deploy/scripts/common.sh
source "${script_dir}/common.sh"
load_deploy_env

cd "$SITE_ROOT"
image_tag="$(resolve_image_tag)"
registry_host="${REGISTRY_HOST:-registry.strawberrycat.dev}"
[[ "$registry_host" =~ ^[A-Za-z0-9.-]+(:[0-9]+)?$ ]] || { echo "Invalid REGISTRY_HOST." >&2; exit 2; }
: "${REGISTRY_ACCESS_TOKEN:?Set REGISTRY_ACCESS_TOKEN in deploy/.env or the environment.}"
backend_image="${BACKEND_IMAGE:-localhost:5000/animestars-extensionsite-backend}"
frontend_image="${FRONTEND_IMAGE:-localhost:5000/animestars-extensionsite-frontend}"
api_url="${VITE_API_URL:-https://ass-api.strawberrycat.dev}"
for image in "$backend_image" "$frontend_image"; do
  [[ "$image" =~ ^[A-Za-z0-9._:/-]+$ ]] || { echo "Invalid image repository override." >&2; exit 2; }
done

docker_config_dir="$(mktemp -d)"
chmod 700 "$docker_config_dir"
export DOCKER_CONFIG="$docker_config_dir"
cleanup() { rm -rf -- "$docker_config_dir"; }
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
printf '%s' "$REGISTRY_ACCESS_TOKEN" | docker login "$registry_host" --username token --password-stdin >/dev/null

backend_path="${backend_image#*/}"
frontend_path="${frontend_image#*/}"
for image_path in "$backend_path" "$frontend_path"; do
  status="$(printf 'user = "token:%s"\n' "$REGISTRY_ACCESS_TOKEN" | curl --config - --silent --show-error --max-time 5 -o /dev/null -w '%{http_code}' \
    -H 'Accept: application/vnd.oci.image.index.v1+json, application/vnd.oci.image.manifest.v1+json, application/vnd.docker.distribution.manifest.list.v2+json, application/vnd.docker.distribution.manifest.v2+json' \
    "https://${registry_host}/v2/${image_path}/manifests/${image_tag}")"
  if [[ "$status" == "200" ]]; then
    echo "Refusing to overwrite existing image tag ${image_path}:${image_tag}. Choose a new IMAGE_TAG." >&2
    exit 2
  elif [[ "$status" != "404" ]]; then
    echo "Could not verify that image tag ${image_path}:${image_tag} is unused (registry returned HTTP ${status})." >&2
    exit 1
  fi
done

docker build -f docker/Dockerfile -t "${backend_image}:${image_tag}" .
docker tag "${backend_image}:${image_tag}" "${registry_host}/${backend_path}:${image_tag}"
docker push "${registry_host}/${backend_path}:${image_tag}"

docker build -f docker/Dockerfile.frontend --target production --build-arg "VITE_API_URL=${api_url}" \
  -t "${frontend_image}:${image_tag}" .
docker tag "${frontend_image}:${image_tag}" "${registry_host}/${frontend_path}:${image_tag}"
docker push "${registry_host}/${frontend_path}:${image_tag}"

echo "Pushed backend and frontend images with tag ${image_tag}."
