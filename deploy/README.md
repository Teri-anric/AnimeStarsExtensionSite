# Deploy (Kubernetes)

This repo uses Terraform to manage Kubernetes resources:
- dev: Kind (local), images loaded into the cluster
- prod: k3s (server), images pushed to a private loopback-only registry on the server (via SSH tunnel)

## Prerequisites
- Docker
- kubectl
- kind (for dev)
- terraform (for dev/prod manifests)

## Host Entry (Optional)

If you want to use `animestars.local` locally, add it to `/etc/hosts`:
```bash
echo "127.0.0.1 animestars.local" | sudo tee -a /etc/hosts
```

## Development (Kind) quick start
```bash
make k8s-dev-up
```

If you don't add the host entry, you can still access via localhost with a Host header:
```bash
curl -H 'Host: animestars.local' http://127.0.0.1/
```

## Production (k3s)

Production is Terraform + Traefik (ACME configured via shared cluster infra) + a private `registry:2` bound to `127.0.0.1` on the server.

Docs:
- `deploy/terraform/README.md`

Typical deploy:
```bash
make k8s-prod-secrets
make k8s-prod-deploy K8S_IMAGE_TAG=$(git rev-parse --short HEAD) K8S_EXTRA_TAGS=prod,latest
```

## Common targets
- `make k8s-dev-up`: Kind + build/load + terraform apply + health checks
- `make k8s-dev-down`: terraform destroy + Kind delete
- `make k8s-prod-deploy`: build + push images + terraform apply (deploys by immutable tag)
- `make k8s-prod-destroy`: terraform destroy
