# AnimeStarsExtensionSite deployment

Deployment is manual from the workstation to the existing two-node s1 K3s cluster. Docker builds run locally and image pushes go through an SSH local forward to the private registry on s1. No GitHub Actions workflow deploys this application.

## Terraform ownership

Terraform owns the application namespace and its Kubernetes resources: PostgreSQL PV/PVC pairs, runtime Secret and ConfigMap, PostgreSQL and Redis services/workloads, backend/frontend/scheduler/mitmproxy services/workloads, the Alembic Job, the app's Traefik IngressRoute, and a ConfigMap containing this project's Grafana dashboards. Shared Grafana infrastructure provisions dashboards from labeled ConfigMaps; the dashboard JSON remains in this repository.

The existing Traefik controller and its `IngressRoute` CRD, registry, Prometheus, Loki, and Grafana remain shared infrastructure. This project creates no copies of those services and manages no DNS records. The Traefik CRD must already be installed and available while Terraform plans the IngressRoute.

Both static PostgreSQL PVs are pinned to `s0.teri` and use reclaim policy `Retain`. Terraform destroy removes the Kubernetes PV/PVC objects and workloads, while the host directories remain on s0:

- Preserved Compose database: `/root/Teri-anric/AnimeStarsExtensionSite/db`
- Active restored database: `/root/Teri-anric/AnimeStarsExtensionSite/db-k8s`
- Pre-cutover dump: `/root/Teri-anric/AnimeStarsExtensionSite/pre-k3s-backup/animestars-20261008T190657Z.dump`

The database restore from the pre-cutover dump is complete. Future schema changes use only the Alembic Job; no restore Job is part of normal deployment. The dashboard JSON files are the source of truth for the three AnimeStars dashboards. Terraform stores them in a ConfigMap labeled `grafana_dashboard=1`; its `k8s-sidecar-target-directory` annotation places the dashboards in the Grafana root folder `Anime Stars`. The shared Grafana sidecar discovers and provisions them. The dashboards keep stable UIDs and refer to the shared Prometheus and Loki datasource UIDs.

Terraform manages the `runtime-secrets` Secret. Its values are marked sensitive in Terraform input/output, but Kubernetes provider state still contains the values. The remote state backend and local plan files must be access-controlled; do not commit `terraform.tfvars`, state, or plan files.

## Workstation setup

1. Copy `deploy/.env.example` to `deploy/.env` and configure the SSH target for s1. The file is ignored by Git. Use the workstation kubeconfig for the s1 cluster, whose context includes s0; defaults are `~/.kube/k3s-s1.yaml` and context `k3s`.
2. Copy `deploy/terraform/backend.hcl.example` to `deploy/terraform/backend.hcl`. It uses the shared Terraform state bucket `terraform-state` at `https://s3.strawberrycat.dev`, with this application's isolated key: `animestars-extensionsite/prod/terraform.tfstate`. Export `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` for that backend.
3. Copy `deploy/terraform/terraform.tfvars.example` to `deploy/terraform/terraform.tfvars`. Replace the runtime Secret placeholders with all current `runtime-secrets` keys and values. Keep the file private and ignored by Git.
4. Run `task tf:validate` for offline Terraform and dashboard-asset validation.

## Adopt the existing cluster resources

The application is already running in K3s. Import its current Kubernetes objects into the dedicated state before applying Terraform changes:

```sh
task prod:tf:init
IMPORT_EXISTING_RESOURCES=true task prod:tf:import
task prod:tf:plan
```

The import task checks the selected context has a Ready `s0.teri`, imports each existing project Kubernetes resource, and reports missing objects that a later plan may create. It skips addresses already in state, so imports can be resumed. It imports the existing runtime Secret; its values are written to the private remote state. The new dashboard ConfigMap is a project Kubernetes resource and is created by Terraform if it does not already exist. A missing Traefik CRD or unreachable cluster will prevent import/plan and must be resolved before applying. Grafana itself does not need to be reachable from the workstation; the shared in-cluster sidecar provisions the ConfigMap contents.

Review the saved plan before applying it. Existing Kubernetes objects should be adopted in place; allow only intentional changes or creation of app resources that are actually absent. The dashboard ConfigMap should be created once and then updated from the checked-in JSON when dashboards change.

## Application release

The image tag defaults to `git rev-parse --short HEAD`, matching the other Strawberry projects. `prod:deploy` builds and pushes both images, then runs Terraform with interactive approval. Terraform applies the runtime, waits for the Alembic Job to succeed, rolls out backend/frontend/scheduler, and applies the app IngressRoute. The migration Job receives a unique Kubernetes name for each deployment run.

```sh
task prod:deploy
```

For a reviewed plan and separate apply, use `task prod:tf:plan` followed by `task prod:tf:apply`. `task prod:apply` applies changes through Terraform and waits for the application workloads; it does not push images. The Kubernetes objects are declared directly in Terraform HCL; do not create a second lifecycle by applying separate YAML manifests.

## Destroy the application resources

```sh
task prod:destroy
```

Terraform prompts before deleting this application's resources. It removes the dashboard ConfigMap along with the application's Kubernetes objects; the shared Grafana sidecar then removes the provisioned dashboard files. The namespace and PV/PVC objects are deleted, while the PV `Retain` policy leaves both PostgreSQL host directories and the pre-cutover dump on s0. The shared Traefik, registry, Prometheus, Loki, and Grafana services remain outside this project's Terraform state.

## Operations

```sh
task prod:status
task prod:logs
task prod:ctl -- get pods
```

Kubernetes context and registry routing can be overridden per invocation with `KUBECONFIG_PATH`, `KUBE_CONTEXT`, `SSH_TARGET`, `REGISTRY_LOCAL_PORT`, and `REGISTRY_REMOTE_PORT`. Never put kubeconfig data, tokens, database credentials, Terraform state, or plans in this repository.
