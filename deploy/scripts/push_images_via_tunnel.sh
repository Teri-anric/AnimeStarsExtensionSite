#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <image_repo_1> <image_repo_2> [<image_repo_3> ...]" >&2
  echo "Env: K8S_IMAGE_TAG, K8S_EXTRA_TAGS, PROD_SSH_TARGET, K8S_REGISTRY_LOCAL_PORT, K8S_REGISTRY_REMOTE_PORT" >&2
  exit 2
fi

TAG="${K8S_IMAGE_TAG:-}"
if [[ -z "${TAG}" ]]; then
  echo "K8S_IMAGE_TAG is required." >&2
  exit 1
fi

EXTRA_TAGS="${K8S_EXTRA_TAGS:-prod,latest}"
SSH_TARGET="${PROD_SSH_TARGET:-${SSH_TARGET:-}}"
if [[ -z "${SSH_TARGET}" ]]; then
  echo "PROD_SSH_TARGET is required (e.g. user@server)." >&2
  exit 1
fi

REGISTRY_LOCAL_PORT="${K8S_REGISTRY_LOCAL_PORT:-5000}"
REGISTRY_REMOTE_PORT="${K8S_REGISTRY_REMOTE_PORT:-5000}"

echo "Starting SSH tunnel to ${SSH_TARGET} (127.0.0.1:${REGISTRY_LOCAL_PORT} -> 127.0.0.1:${REGISTRY_REMOTE_PORT})..."
ssh -o ExitOnForwardFailure=yes -N \
  -L "${REGISTRY_LOCAL_PORT}:127.0.0.1:${REGISTRY_REMOTE_PORT}" \
  "${SSH_TARGET}" &
TUNNEL_PID=$!
trap 'kill "${TUNNEL_PID}" 2>/dev/null || true' EXIT

for i in $(seq 1 20); do
  if command -v curl >/dev/null 2>&1; then
    if curl -sf --max-time 1 "http://127.0.0.1:${REGISTRY_LOCAL_PORT}/v2/" >/dev/null 2>&1; then
      break
    fi
  else
    if timeout 1 bash -c "echo >/dev/tcp/127.0.0.1/${REGISTRY_LOCAL_PORT}" 2>/dev/null; then
      break
    fi
  fi
  if [[ $i -eq 20 ]]; then
    echo "Registry not reachable on 127.0.0.1:${REGISTRY_LOCAL_PORT} (via SSH tunnel)." >&2
    exit 1
  fi
  sleep 0.25
done

TAGS="${TAG},${EXTRA_TAGS}"
OLD_IFS="${IFS}"
IFS=','
for t in ${TAGS}; do
  IFS="${OLD_IFS}"
  t="$(echo "${t}" | xargs)"
  [[ -z "${t}" ]] && continue

  for repo in "$@"; do
    local_image="${repo}:${TAG}"
    remote_image="127.0.0.1:${REGISTRY_LOCAL_PORT}/${repo}:${t}"

    docker image tag "${local_image}" "${remote_image}"
    docker image push "${remote_image}"
  done
done
IFS="${OLD_IFS}"
