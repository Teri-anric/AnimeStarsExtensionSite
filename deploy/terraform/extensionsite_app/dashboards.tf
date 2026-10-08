# The shared Grafana dashboard sidecar watches ConfigMaps carrying this label.
# Keep the payload in this project's namespace and use project-prefixed filenames
# so the shared provisioner can safely collect dashboards from every namespace.
resource "kubernetes_config_map_v1" "grafana_dashboards" {
  metadata {
    name      = "animestars-grafana-dashboards"
    namespace = kubernetes_namespace_v1.site.metadata[0].name
    annotations = {
      "k8s-sidecar-target-directory" = "/var/lib/grafana/dashboards/Anime Stars"
    }
    labels = merge(local.common_labels, {
      grafana_dashboard = "1"
    })
  }

  data = {
    "animestars-backend-overview.json" = file("${path.module}/../../dashboards/backend-overview.json")
    "animestars-db-sqlalchemy.json"    = file("${path.module}/../../dashboards/db-sqlalchemy.json")
    "animestars-logs-loki.json"        = file("${path.module}/../../dashboards/logs-loki.json")
  }
}
