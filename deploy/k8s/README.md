# Kubernetes deployment assets

The active application resources are declared directly as typed Terraform resources in `../terraform/`, split by responsibility across runtime, storage, app, migration, and ingress files. Use the project Taskfile to plan/apply/destroy them; there are no active Kubernetes YAML manifests to apply separately.

`../dashboards/` contains the JSON source files for this project's Grafana dashboards. Terraform copies them into the app namespace ConfigMap in `../terraform/extensionsite_app/dashboards.tf`, labeled `grafana_dashboard=1` for the shared Grafana sidecar to discover. The ConfigMap's `k8s-sidecar-target-directory` annotation maps them into Grafana's root folder `Anime Stars`. Shared infrastructure provides the generic Grafana provisioning mechanism; this project does not create Grafana or its Prometheus/Loki datasources. PostgreSQL runs on the K3s local-path PVC managed by the app Terraform configuration.
