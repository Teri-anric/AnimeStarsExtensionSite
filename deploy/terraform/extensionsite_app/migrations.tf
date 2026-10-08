resource "kubernetes_job_v1" "alembic" {
  metadata {
    name      = var.migration_job_name
    namespace = kubernetes_namespace_v1.site.metadata[0].name
    labels = merge(local.common_labels, {
      "app.kubernetes.io/name" = "animestars-extension-site-migrations"
    })
  }

  wait_for_completion = true

  spec {
    backoff_limit           = 1
    active_deadline_seconds = 600
    template {
      metadata {
        labels = { "app.kubernetes.io/name" = "animestars-extension-site-migrations" }
      }
      spec {
        restart_policy = "Never"
        node_selector  = { "kubernetes.io/hostname" = var.node_name }
        init_container {
          name              = "wait-for-postgres"
          image             = var.postgres_image
          image_pull_policy = "IfNotPresent"
          command           = ["sh", "-c", "until pg_isready -h postgres -p 5432 -U \"$DATABASE__USER\" -d \"$DATABASE__DB\"; do sleep 2; done"]
          env_from {
            config_map_ref { name = kubernetes_config_map_v1.runtime.metadata[0].name }
          }
          env_from {
            secret_ref { name = kubernetes_secret_v1.runtime.metadata[0].name }
          }
          resources {
            requests = { cpu = "25m", memory = "32Mi" }
            limits   = { cpu = "100m", memory = "128Mi" }
          }
        }
        container {
          name              = "alembic"
          image             = var.backend_image
          image_pull_policy = "IfNotPresent"
          command           = ["alembic", "upgrade", "head"]
          env_from {
            config_map_ref { name = kubernetes_config_map_v1.runtime.metadata[0].name }
          }
          env_from {
            secret_ref { name = kubernetes_secret_v1.runtime.metadata[0].name }
          }
          resources {
            requests = { cpu = "100m", memory = "256Mi" }
            limits   = { cpu = "500m", memory = "768Mi" }
          }
        }
      }
    }
  }

  timeouts { create = "15m" }
  depends_on = [
    kubernetes_stateful_set_v1.postgres,
    kubernetes_deployment_v1.redis,
  ]
}
