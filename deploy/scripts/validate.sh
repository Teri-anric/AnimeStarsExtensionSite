#!/usr/bin/env bash
set -euo pipefail
set +x

script_dir="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=deploy/scripts/common.sh
source "${script_dir}/common.sh"

terraform -chdir="$TERRAFORM_ROOT" fmt -check -recursive
tf_data="$(mktemp -d)"
trap 'rm -rf "$tf_data"' EXIT
TF_DATA_DIR="$tf_data" terraform -chdir="$TERRAFORM_ROOT" init -backend=false -input=false
TF_DATA_DIR="$tf_data" terraform -chdir="$TERRAFORM_ROOT" validate

python3 - "$DEPLOY_ROOT" <<'PY'
import json
import sys
from pathlib import Path

deploy_root = Path(sys.argv[1])
dashboard_dir = deploy_root / "dashboards"
paths = sorted(dashboard_dir.glob("*.json"))
if not paths:
    raise SystemExit("No Grafana dashboard JSON files found")
for path in paths:
    with path.open(encoding="utf-8") as stream:
        dashboard = json.load(stream)
    if not isinstance(dashboard, dict) or not dashboard.get("title"):
        raise SystemExit(f"Invalid Grafana dashboard payload: {path}")
    print(f"Dashboard JSON OK: {path.relative_to(deploy_root.parent)}")
PY
