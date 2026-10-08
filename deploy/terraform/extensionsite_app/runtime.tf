resource "kubernetes_secret_v1" "runtime" {
  metadata {
    name      = "runtime-secrets"
    namespace = kubernetes_namespace_v1.site.metadata[0].name
    labels    = local.common_labels
  }

  data = var.runtime_secret_data
  type = "Opaque"
}

resource "kubernetes_config_map_v1" "runtime" {
  metadata {
    name      = "runtime-config"
    namespace = kubernetes_namespace_v1.site.metadata[0].name
    labels    = local.common_labels
  }

  data = {
    DATABASE__HOST  = "postgres"
    DATABASE__PORT  = "5432"
    REDIS__HOST     = "redis"
    REDIS__PORT     = "6379"
    PARSER__PROXY   = "socks5://mitmproxy:8080"
    LOG_JSON        = "true"
    LOG_HTTP_BODIES = "false"
  }
}

resource "kubernetes_service_v1" "postgres" {
  metadata {
    name      = "postgres"
    namespace = kubernetes_namespace_v1.site.metadata[0].name
    labels    = local.labels.postgres
  }

  spec {
    type     = "ClusterIP"
    selector = { "app.kubernetes.io/name" = "postgres" }

    port {
      name        = "postgres"
      port        = 5432
      target_port = "postgres"
    }
  }
}

resource "kubernetes_stateful_set_v1" "postgres" {
  metadata {
    name      = "postgres"
    namespace = kubernetes_namespace_v1.site.metadata[0].name
    labels    = local.labels.postgres
  }

  spec {
    service_name = kubernetes_service_v1.postgres.metadata[0].name
    replicas     = 1

    selector { match_labels = { "app.kubernetes.io/name" = "postgres" } }

    template {
      metadata {
        labels = merge(local.labels.postgres, { "app.kubernetes.io/name" = "postgres" })
      }

      spec {
        node_selector                    = { "kubernetes.io/hostname" = var.node_name }
        termination_grace_period_seconds = 60

        container {
          name              = "postgres"
          image             = var.postgres_image
          image_pull_policy = "IfNotPresent"

          port {
            name           = "postgres"
            container_port = 5432
          }

          env {
            name = "POSTGRES_USER"
            value_from {
              secret_key_ref {
                name = kubernetes_secret_v1.runtime.metadata[0].name
                key  = "DATABASE__USER"
              }
            }
          }
          env {
            name = "POSTGRES_PASSWORD"
            value_from {
              secret_key_ref {
                name = kubernetes_secret_v1.runtime.metadata[0].name
                key  = "DATABASE__PASSWORD"
              }
            }
          }
          env {
            name = "POSTGRES_DB"
            value_from {
              secret_key_ref {
                name = kubernetes_secret_v1.runtime.metadata[0].name
                key  = "DATABASE__DB"
              }
            }
          }

          volume_mount {
            name       = "postgres-data"
            mount_path = "/var/lib/postgresql/data"
          }

          startup_probe {
            exec { command = ["sh", "-c", "pg_isready -U \"$POSTGRES_USER\" -d \"$POSTGRES_DB\""] }
            period_seconds    = 10
            timeout_seconds   = 5
            failure_threshold = 60
          }
          readiness_probe {
            exec { command = ["sh", "-c", "pg_isready -U \"$POSTGRES_USER\" -d \"$POSTGRES_DB\""] }
            period_seconds  = 10
            timeout_seconds = 5
          }
          liveness_probe {
            exec { command = ["sh", "-c", "pg_isready -U \"$POSTGRES_USER\" -d \"$POSTGRES_DB\""] }
            period_seconds    = 20
            timeout_seconds   = 5
            failure_threshold = 6
          }

          resources {
            requests = { cpu = "250m", memory = "512Mi" }
            limits   = { cpu = "1", memory = "2Gi" }
          }
        }

        volume {
          name = "postgres-data"
          persistent_volume_claim {
            claim_name = kubernetes_persistent_volume_claim_v1.active_postgres.metadata[0].name
          }
        }
      }
    }
  }

  wait_for_rollout = false

  depends_on = [
    kubernetes_secret_v1.runtime,
    kubernetes_persistent_volume_claim_v1.active_postgres,
  ]
}

resource "kubernetes_service_v1" "redis" {
  metadata {
    name      = "redis"
    namespace = kubernetes_namespace_v1.site.metadata[0].name
    labels    = local.labels.redis
  }

  spec {
    type     = "ClusterIP"
    selector = { "app.kubernetes.io/name" = "redis" }

    port {
      name        = "redis"
      port        = 6379
      target_port = "redis"
    }
  }
}

resource "kubernetes_deployment_v1" "redis" {
  metadata {
    name      = "redis"
    namespace = kubernetes_namespace_v1.site.metadata[0].name
    labels    = local.labels.redis
  }

  spec {
    replicas = 1
    selector { match_labels = { "app.kubernetes.io/name" = "redis" } }
    strategy { type = "Recreate" }

    template {
      metadata { labels = local.labels.redis }
      spec {
        node_selector = { "kubernetes.io/hostname" = var.node_name }
        container {
          name              = "redis"
          image             = var.redis_image
          image_pull_policy = "IfNotPresent"
          command           = ["redis-server", "--save", "", "--appendonly", "no"]

          port {
            name           = "redis"
            container_port = 6379
          }
          readiness_probe {
            exec { command = ["redis-cli", "ping"] }
            period_seconds = 5
          }
          liveness_probe {
            exec { command = ["redis-cli", "ping"] }
            period_seconds = 15
          }
          resources {
            requests = { cpu = "50m", memory = "64Mi" }
            limits   = { cpu = "500m", memory = "256Mi" }
          }
        }
      }
    }
  }

  wait_for_rollout = false
  depends_on       = [kubernetes_service_v1.redis]
}

resource "kubernetes_service_v1" "mitmproxy" {
  metadata {
    name      = "mitmproxy"
    namespace = kubernetes_namespace_v1.site.metadata[0].name
    labels    = local.labels.mitmproxy
  }

  spec {
    type     = "ClusterIP"
    selector = { "app.kubernetes.io/name" = "mitmproxy" }

    port {
      name        = "socks5"
      port        = 8080
      target_port = "socks5"
    }
  }
}

resource "kubernetes_deployment_v1" "mitmproxy" {
  metadata {
    name      = "mitmproxy"
    namespace = kubernetes_namespace_v1.site.metadata[0].name
    labels    = local.labels.mitmproxy
  }

  spec {
    replicas = 1
    selector { match_labels = { "app.kubernetes.io/name" = "mitmproxy" } }
    template {
      metadata { labels = local.labels.mitmproxy }
      spec {
        node_selector = { "kubernetes.io/hostname" = var.node_name }
        container {
          name              = "mitmproxy"
          image             = var.mitmproxy_image
          image_pull_policy = "IfNotPresent"
          command           = ["mitmdump", "--mode", "socks5", "--listen-host", "0.0.0.0", "--listen-port", "8080", "--set", "block_global=false", "--set", "ssl_insecure=true"]
          port {
            name           = "socks5"
            container_port = 8080
          }
          resources {
            requests = { cpu = "50m", memory = "64Mi" }
            limits   = { cpu = "500m", memory = "512Mi" }
          }
        }
      }
    }
  }

  wait_for_rollout = false
  depends_on       = [kubernetes_service_v1.mitmproxy]
}
