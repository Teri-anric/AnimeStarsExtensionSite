resource "kubernetes_service_v1" "backend" {
  metadata {
    name      = "backend"
    namespace = kubernetes_namespace_v1.site.metadata[0].name
    labels    = local.labels.backend
  }

  spec {
    type     = "ClusterIP"
    selector = { "app.kubernetes.io/name" = "backend" }
    port {
      name        = "http"
      port        = 8000
      target_port = "http"
    }
  }
}

resource "kubernetes_deployment_v1" "backend" {
  metadata {
    name      = "backend"
    namespace = kubernetes_namespace_v1.site.metadata[0].name
    labels    = local.labels.backend
  }

  wait_for_rollout = false

  # KEDA owns the live replica count after creation, including scale-to-zero.
  lifecycle {
    ignore_changes = [spec[0].replicas]
  }

  spec {
    replicas = 1
    selector { match_labels = { "app.kubernetes.io/name" = "backend" } }

    template {
      metadata {
        labels = local.labels.backend
        annotations = merge({
          "prometheus.io/scrape" = "true"
          "prometheus.io/port"   = "8000"
          "prometheus.io/path"   = "/metrics"
        }, local.runtime_config_checksum_annotation)
      }

      spec {
        # These HTTP workloads must be schedulable on either node when KEDA
        # wakes them; pinning them to the busy worker can leave cold requests pending.

        container {
          name              = "backend"
          image             = var.backend_image
          image_pull_policy = "IfNotPresent"
          command           = ["sh", "-c"]
          args              = ["mkdir -p /tmp/prometheus_multiproc && rm -f /tmp/prometheus_multiproc/* && python -m uvicorn app.web:app --host 0.0.0.0 --port 8000 --workers 2"]

          port {
            name           = "http"
            container_port = 8000
          }
          env_from {
            config_map_ref { name = kubernetes_config_map_v1.runtime.metadata[0].name }
          }
          env_from {
            secret_ref { name = kubernetes_secret_v1.runtime.metadata[0].name }
          }
          env {
            name  = "PROMETHEUS_MULTIPROC_DIR"
            value = "/tmp/prometheus_multiproc"
          }
          volume_mount {
            name       = "prometheus-multiproc"
            mount_path = "/tmp/prometheus_multiproc"
          }
          startup_probe {
            http_get {
              path = "/ready"
              port = "http"
            }
            period_seconds    = 5
            timeout_seconds   = 3
            failure_threshold = 60
          }
          readiness_probe {
            http_get {
              path = "/ready"
              port = "http"
            }
            period_seconds  = 10
            timeout_seconds = 3
          }
          liveness_probe {
            http_get {
              path = "/health"
              port = "http"
            }
            period_seconds  = 30
            timeout_seconds = 3
          }
          resources {
            requests = { cpu = "200m", memory = "512Mi" }
            limits   = { cpu = "2", memory = "1536Mi" }
          }
        }

        volume {
          name = "prometheus-multiproc"
          empty_dir { size_limit = "128Mi" }
        }
      }
    }
  }

  depends_on = [kubernetes_job_v1.alembic]
}

resource "kubernetes_service_v1" "frontend" {
  metadata {
    name      = "frontend"
    namespace = kubernetes_namespace_v1.site.metadata[0].name
    labels    = local.labels.frontend
  }

  spec {
    type     = "ClusterIP"
    selector = { "app.kubernetes.io/name" = "frontend" }
    port {
      name        = "http"
      port        = 8080
      target_port = "http"
    }
  }
}

resource "kubernetes_deployment_v1" "frontend" {
  metadata {
    name      = "frontend"
    namespace = kubernetes_namespace_v1.site.metadata[0].name
    labels    = local.labels.frontend
  }

  wait_for_rollout = false

  # KEDA owns the live replica count after creation, including scale-to-zero.
  lifecycle {
    ignore_changes = [spec[0].replicas]
  }

  spec {
    replicas = 1
    selector { match_labels = { "app.kubernetes.io/name" = "frontend" } }
    template {
      metadata {
        labels      = local.labels.frontend
        annotations = length(local.runtime_config_checksum_annotation) > 0 ? local.runtime_config_checksum_annotation : null
      }
      spec {
        # Keep the scale-to-zero frontend schedulable on either node at wake-up.
        container {
          name              = "frontend"
          image             = var.frontend_image
          image_pull_policy = "IfNotPresent"
          port {
            name           = "http"
            container_port = 8080
          }
          readiness_probe {
            http_get {
              path = "/"
              port = "http"
            }
            period_seconds  = 10
            timeout_seconds = 3
          }
          liveness_probe {
            http_get {
              path = "/"
              port = "http"
            }
            period_seconds  = 30
            timeout_seconds = 3
          }
          resources {
            requests = { cpu = "25m", memory = "32Mi" }
            limits   = { cpu = "200m", memory = "128Mi" }
          }
        }
      }
    }
  }

}

resource "kubernetes_deployment_v1" "scheduler" {
  metadata {
    name      = "scheduler"
    namespace = kubernetes_namespace_v1.site.metadata[0].name
    labels    = local.labels.scheduler
  }

  wait_for_rollout = false

  spec {
    replicas = 1
    selector { match_labels = { "app.kubernetes.io/name" = "scheduler" } }
    strategy { type = "Recreate" }

    template {
      metadata {
        labels      = local.labels.scheduler
        annotations = length(local.runtime_config_checksum_annotation) > 0 ? local.runtime_config_checksum_annotation : null
      }
      spec {
        node_selector                    = { "kubernetes.io/hostname" = var.node_name }
        termination_grace_period_seconds = 60
        container {
          name              = "scheduler"
          image             = var.backend_image
          image_pull_policy = "IfNotPresent"
          command           = ["python", "-m", "app.scheduler"]
          env_from {
            config_map_ref { name = kubernetes_config_map_v1.runtime.metadata[0].name }
          }
          env_from {
            secret_ref { name = kubernetes_secret_v1.runtime.metadata[0].name }
          }
          resources {
            requests = { cpu = "50m", memory = "256Mi" }
            limits   = { cpu = "500m", memory = "512Mi" }
          }
        }
      }
    }
  }

  depends_on = [kubernetes_job_v1.alembic]
}
