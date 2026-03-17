# Terraform Deploy

This directory contains a Terraform-based deploy for AnimeStarsExtensionSite.

Goals:
- Manage Kubernetes resources (prod on k3s, optional dev on Kind) via Terraform
- Switch prod image delivery to a private registry:2 bound to k3s node loopback (no public access)

Quick links:
- `deploy/terraform/prod` - production (k3s) stack
- `deploy/terraform/dev` - development (Kind) stack

Notes:
- Terraform state will contain Kubernetes secret values (e.g. `POSTGRES_PASSWORD`). Use a secure backend/state workflow if needed.

## Production (k3s)

What you get:
- Traefik ingress for the app (ACME/TLS handled by shared cluster infra)
- app stack (postgres + backend + frontend + ingress)

Note: The loopback-only registry (e.g. `registry:2` on `127.0.0.1:5000` on the k3s node) is expected to be managed outside of this repo.

### 1) Deploy infrastructure + app manifests

Create tfvars (recommended):
```bash
make k8s-prod-secrets
```

Then from this repo on your machine:
```bash
cd deploy/terraform/prod
terraform init
terraform apply \
  -var kubeconfig_path=/path/to/kubeconfig \
  -auto-approve
```

By default, prod images are expected at:
- `localhost:5000/animestars/backend:prod`
- `localhost:5000/animestars/frontend:prod`

### 2) Push images into the private registry (via SSH tunnel)

The registry is loopback-only on the server, so push via an SSH local forward:
```bash
IMAGE_TAG=$(git rev-parse --short HEAD)
make k8s-prod-build K8S_IMAGE_TAG=$IMAGE_TAG
make k8s-prod-push K8S_IMAGE_TAG=$IMAGE_TAG K8S_EXTRA_TAGS=prod,latest
```

If your local Docker daemon refuses pushing to `localhost:5000` over HTTP, add it to Docker "insecure registries" on your machine.

Re-apply Terraform whenever you change image tags/vars:
```bash
cd deploy/terraform/prod
terraform apply
```

## Development (Kind)

Dev Terraform deploy assumes:
- You still use the existing Kind scripts in `deploy/` to create the cluster and load images
- Terraform manages the app stack resources (and installs a minimal Traefik for Kind by default)

Example:
```bash
make k8s-dev-kind-create
make k8s-dev-build
make k8s-dev-load

cd ../deploy/terraform/dev
terraform init
terraform apply \
  -var kubeconfig_path=~/.kube/config \
  -var postgres_password=devpassword \
  -auto-approve
```
