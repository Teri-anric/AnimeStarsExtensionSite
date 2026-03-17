terraform {
  required_version = ">= 1.5.0"

  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = ">= 2.20.0"
    }
  }
}

locals {
  app_labels = {
    "app.kubernetes.io/part-of" = "animestars"
  }

  backend_labels   = merge(local.app_labels, { "app.kubernetes.io/name" = "backend" })
  scheduler_labels = merge(local.app_labels, { "app.kubernetes.io/name" = "scheduler" })
  frontend_labels  = merge(local.app_labels, { "app.kubernetes.io/name" = "frontend" })
  postgres_labels  = merge(local.app_labels, { "app.kubernetes.io/name" = "postgres" })
  proxy_labels     = merge(local.app_labels, { "app.kubernetes.io/name" = "proxy" })
}

resource "kubernetes_namespace_v1" "this" {
  metadata {
    name = var.namespace
    labels = {
      name = var.namespace
    }
  }
}

resource "kubernetes_secret_v1" "postgres" {
  metadata {
    name      = "postgres-secret"
    namespace = kubernetes_namespace_v1.this.metadata[0].name
  }

  type = "Opaque"

  data = {
    POSTGRES_PASSWORD = base64encode(var.postgres_password)
  }
}

resource "kubernetes_service_account_v1" "backend" {
  metadata {
    name      = "backend"
    namespace = kubernetes_namespace_v1.this.metadata[0].name
  }
}

resource "kubernetes_role_v1" "backend_job_manager" {
  metadata {
    name      = "backend-job-manager"
    namespace = kubernetes_namespace_v1.this.metadata[0].name
  }

  rule {
    api_groups = ["batch"]
    resources  = ["jobs"]
    verbs      = ["create", "get", "list", "watch", "delete", "patch", "update"]
  }

  rule {
    api_groups = [""]
    resources  = ["pods"]
    verbs      = ["get", "list", "watch"]
  }
}

resource "kubernetes_role_binding_v1" "backend_job_manager" {
  metadata {
    name      = "backend-job-manager-binding"
    namespace = kubernetes_namespace_v1.this.metadata[0].name
  }

  subject {
    kind      = "ServiceAccount"
    name      = kubernetes_service_account_v1.backend.metadata[0].name
    namespace = kubernetes_namespace_v1.this.metadata[0].name
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "Role"
    name      = kubernetes_role_v1.backend_job_manager.metadata[0].name
  }
}

resource "kubernetes_service_v1" "postgres" {
  metadata {
    name      = "postgres"
    namespace = kubernetes_namespace_v1.this.metadata[0].name
    labels    = local.postgres_labels
  }

  spec {
    selector = local.postgres_labels

    port {
      name        = "postgres"
      port        = 5432
      target_port = 5432
      protocol    = "TCP"
    }

    type = "ClusterIP"
  }
}

resource "kubernetes_service_v1" "proxy" {
  count = var.enable_proxy ? 1 : 0

  metadata {
    name      = "proxy"
    namespace = kubernetes_namespace_v1.this.metadata[0].name
    labels    = local.proxy_labels
  }

  spec {
    selector = local.proxy_labels

    port {
      name        = "socks5"
      port        = 8080
      target_port = "socks5"
      protocol    = "TCP"
    }

    type = "ClusterIP"
  }
}

resource "kubernetes_deployment_v1" "proxy" {
  count = var.enable_proxy ? 1 : 0

  metadata {
    name      = "proxy"
    namespace = kubernetes_namespace_v1.this.metadata[0].name
    labels    = local.proxy_labels
  }

  wait_for_rollout = false

  spec {
    replicas = 1

    selector {
      match_labels = local.proxy_labels
    }

    template {
      metadata {
        labels = local.proxy_labels
      }

      spec {
        security_context {
          seccomp_profile {
            type = "RuntimeDefault"
          }
        }

        container {
          name              = "proxy"
          image             = var.proxy_image
          image_pull_policy = "IfNotPresent"

          command = ["mitmdump"]
          args = [
            "--mode",
            "socks5",
            "--listen-host",
            "0.0.0.0",
            "--listen-port",
            "8080",
            "--set",
            "block_global=false",
            "--set",
            "ssl_insecure=true",
          ]

          port {
            name           = "socks5"
            container_port = 8080
          }

          security_context {
            allow_privilege_escalation = false
            capabilities {
              drop = ["ALL"]
            }
          }

          readiness_probe {
            tcp_socket {
              port = "socks5"
            }
            period_seconds        = 5
            initial_delay_seconds = 2
          }

          liveness_probe {
            tcp_socket {
              port = "socks5"
            }
            period_seconds        = 10
            initial_delay_seconds = 5
          }
        }
      }
    }
  }
}

resource "kubernetes_stateful_set_v1" "postgres" {
  metadata {
    name      = "postgres"
    namespace = kubernetes_namespace_v1.this.metadata[0].name
    labels    = local.postgres_labels
  }

  spec {
    service_name = kubernetes_service_v1.postgres.metadata[0].name
    replicas     = 1

    selector {
      match_labels = local.postgres_labels
    }

    template {
      metadata {
        labels = local.postgres_labels
      }

      spec {
        security_context {
          fs_group = 999
          seccomp_profile {
            type = "RuntimeDefault"
          }
        }

        container {
          name              = "postgres"
          image             = "postgres:16-alpine"
          image_pull_policy = "IfNotPresent"

          port {
            name           = "postgres"
            container_port = 5432
          }

          env {
            name  = "POSTGRES_DB"
            value = var.postgres_db
          }
          env {
            name  = "POSTGRES_USER"
            value = var.postgres_user
          }
          env {
            name = "POSTGRES_PASSWORD"
            value_from {
              secret_key_ref {
                name = kubernetes_secret_v1.postgres.metadata[0].name
                key  = "POSTGRES_PASSWORD"
              }
            }
          }

          readiness_probe {
            exec {
              command = ["sh", "-c", "pg_isready -U $${POSTGRES_USER}"]
            }
            initial_delay_seconds = 10
            period_seconds        = 10
            timeout_seconds       = 5
            failure_threshold     = 6
          }

          liveness_probe {
            exec {
              command = ["sh", "-c", "pg_isready -U $${POSTGRES_USER}"]
            }
            initial_delay_seconds = 20
            period_seconds        = 20
            timeout_seconds       = 5
            failure_threshold     = 6
          }

          volume_mount {
            name       = "pgdata"
            mount_path = "/var/lib/postgresql/data"
          }
        }
      }
    }

    volume_claim_template {
      metadata {
        name = "pgdata"
      }

      spec {
        access_modes = ["ReadWriteOnce"]
        resources {
          requests = {
            storage = var.postgres_storage
          }
        }
      }
    }
  }
}

resource "kubernetes_service_v1" "backend" {
  metadata {
    name      = "backend"
    namespace = kubernetes_namespace_v1.this.metadata[0].name
    labels    = local.backend_labels
  }

  spec {
    selector = local.backend_labels

    port {
      name        = "http"
      port        = 8000
      target_port = "http"
      protocol    = "TCP"
    }

    type = "ClusterIP"
  }
}

resource "kubernetes_deployment_v1" "backend" {
  metadata {
    name      = "backend"
    namespace = kubernetes_namespace_v1.this.metadata[0].name
    labels    = local.backend_labels
  }

  wait_for_rollout = false

  spec {
    replicas = 1

    selector {
      match_labels = local.backend_labels
    }

    template {
      metadata {
        labels = local.backend_labels
      }

      spec {
        service_account_name            = kubernetes_service_account_v1.backend.metadata[0].name
        automount_service_account_token = true

        security_context {
          seccomp_profile {
            type = "RuntimeDefault"
          }
        }

        init_container {
          name              = "backend-migrations"
          image             = "${var.backend_image}:${var.backend_tag}"
          image_pull_policy = "IfNotPresent"
          command           = ["sh", "-c"]
          args              = ["python -m alembic upgrade head"]

          security_context {
            allow_privilege_escalation = false
            capabilities {
              drop = ["ALL"]
            }
          }

          env {
            name  = "DATABASE__HOST"
            value = kubernetes_service_v1.postgres.metadata[0].name
          }
          env {
            name  = "DATABASE__PORT"
            value = "5432"
          }
          env {
            name  = "DATABASE__DB"
            value = var.postgres_db
          }
          env {
            name  = "DATABASE__USER"
            value = var.postgres_user
          }
          env {
            name = "DATABASE__PASSWORD"
            value_from {
              secret_key_ref {
                name = kubernetes_secret_v1.postgres.metadata[0].name
                key  = "POSTGRES_PASSWORD"
              }
            }
          }

          dynamic "env" {
            for_each = var.parser_proxy == null ? [] : [var.parser_proxy]
            content {
              name  = "PARSER__PROXY"
              value = env.value
            }
          }

          dynamic "env" {
            for_each = var.parser_base_url == null ? [] : [var.parser_base_url]
            content {
              name  = "PARSER__BASE_URL"
              value = env.value
            }
          }
        }

        container {
          name              = "backend"
          image             = "${var.backend_image}:${var.backend_tag}"
          image_pull_policy = "IfNotPresent"
          command           = ["python", "-m", "uvicorn", "app.web:app", "--host", "0.0.0.0", "--port", "8000"]

          port {
            name           = "http"
            container_port = 8000
          }

          security_context {
            allow_privilege_escalation = false
            capabilities {
              drop = ["ALL"]
            }
          }

          env {
            name  = "DATABASE__HOST"
            value = kubernetes_service_v1.postgres.metadata[0].name
          }
          env {
            name  = "DATABASE__PORT"
            value = "5432"
          }
          env {
            name  = "DATABASE__DB"
            value = var.postgres_db
          }
          env {
            name  = "DATABASE__USER"
            value = var.postgres_user
          }
          env {
            name = "DATABASE__PASSWORD"
            value_from {
              secret_key_ref {
                name = kubernetes_secret_v1.postgres.metadata[0].name
                key  = "POSTGRES_PASSWORD"
              }
            }
          }

          dynamic "env" {
            for_each = var.parser_proxy == null ? [] : [var.parser_proxy]
            content {
              name  = "PARSER__PROXY"
              value = env.value
            }
          }

          dynamic "env" {
            for_each = var.parser_base_url == null ? [] : [var.parser_base_url]
            content {
              name  = "PARSER__BASE_URL"
              value = env.value
            }
          }

          readiness_probe {
            http_get {
              path = "/health"
              port = "http"
            }
            period_seconds        = 5
            initial_delay_seconds = 5
          }

          liveness_probe {
            http_get {
              path = "/health"
              port = "http"
            }
            period_seconds        = 10
            initial_delay_seconds = 10
          }

          resources {
            requests = {
              cpu    = "50m"
              memory = "64Mi"
            }
            limits = {
              cpu    = "500m"
              memory = "256Mi"
            }
          }
        }
      }
    }
  }
}

resource "kubernetes_deployment_v1" "scheduler" {
  count = var.enable_scheduler ? 1 : 0

  metadata {
    name      = "scheduler"
    namespace = kubernetes_namespace_v1.this.metadata[0].name
    labels    = local.scheduler_labels
  }

  wait_for_rollout = false

  spec {
    replicas = 1

    selector {
      match_labels = local.scheduler_labels
    }

    template {
      metadata {
        labels = local.scheduler_labels
      }

      spec {
        security_context {
          seccomp_profile {
            type = "RuntimeDefault"
          }
        }

        container {
          name              = "scheduler"
          image             = "${var.backend_image}:${var.backend_tag}"
          image_pull_policy = "IfNotPresent"

          command = ["python", "-m", "app.scheduler"]

          security_context {
            allow_privilege_escalation = false
            capabilities {
              drop = ["ALL"]
            }
          }

          env {
            name  = "DATABASE__HOST"
            value = kubernetes_service_v1.postgres.metadata[0].name
          }
          env {
            name  = "DATABASE__PORT"
            value = "5432"
          }
          env {
            name  = "DATABASE__DB"
            value = var.postgres_db
          }
          env {
            name  = "DATABASE__USER"
            value = var.postgres_user
          }
          env {
            name = "DATABASE__PASSWORD"
            value_from {
              secret_key_ref {
                name = kubernetes_secret_v1.postgres.metadata[0].name
                key  = "POSTGRES_PASSWORD"
              }
            }
          }

          dynamic "env" {
            for_each = var.parser_proxy == null ? [] : [var.parser_proxy]
            content {
              name  = "PARSER__PROXY"
              value = env.value
            }
          }

          dynamic "env" {
            for_each = var.parser_base_url == null ? [] : [var.parser_base_url]
            content {
              name  = "PARSER__BASE_URL"
              value = env.value
            }
          }
        }
      }
    }
  }
}

resource "kubernetes_service_v1" "frontend" {
  metadata {
    name      = "frontend"
    namespace = kubernetes_namespace_v1.this.metadata[0].name
    labels    = local.frontend_labels
  }

  spec {
    selector = local.frontend_labels

    port {
      name        = "http"
      port        = 80
      target_port = "http"
      protocol    = "TCP"
    }

    type = "ClusterIP"
  }
}

resource "kubernetes_deployment_v1" "frontend" {
  metadata {
    name      = "frontend"
    namespace = kubernetes_namespace_v1.this.metadata[0].name
    labels    = local.frontend_labels
  }

  wait_for_rollout = false

  spec {
    replicas = 1

    selector {
      match_labels = local.frontend_labels
    }

    template {
      metadata {
        labels = local.frontend_labels
      }

      spec {
        security_context {
          seccomp_profile {
            type = "RuntimeDefault"
          }
        }

        container {
          name              = "frontend"
          image             = "${var.frontend_image}:${var.frontend_tag}"
          image_pull_policy = "IfNotPresent"

          port {
            name           = "http"
            container_port = 80
          }

          security_context {
            allow_privilege_escalation = false
            capabilities {
              drop = ["ALL"]
            }
          }

          readiness_probe {
            http_get {
              path = "/"
              port = "http"
            }
            period_seconds        = 5
            initial_delay_seconds = 5
          }

          liveness_probe {
            http_get {
              path = "/"
              port = "http"
            }
            period_seconds        = 10
            initial_delay_seconds = 10
          }

          resources {
            requests = {
              cpu    = "50m"
              memory = "64Mi"
            }
            limits = {
              cpu    = "500m"
              memory = "256Mi"
            }
          }
        }
      }
    }
  }
}

resource "kubernetes_ingress_v1" "animestars" {
  metadata {
    name      = "animestars"
    namespace = kubernetes_namespace_v1.this.metadata[0].name

    annotations = var.enable_tls ? {
      # Use Traefik's built-in ACME (certResolver) instead of cert-manager.
      "traefik.ingress.kubernetes.io/router.entrypoints"      = "websecure"
      "traefik.ingress.kubernetes.io/router.tls"              = "true"
      "traefik.ingress.kubernetes.io/router.tls.certresolver" = var.traefik_certresolver
    } : {}
  }

  spec {
    ingress_class_name = var.ingress_class

    rule {
      host = var.host

      http {
        path {
          path      = "/api"
          path_type = "Prefix"
          backend {
            service {
              name = kubernetes_service_v1.backend.metadata[0].name
              port {
                number = 8000
              }
            }
          }
        }

        path {
          path      = "/"
          path_type = "Prefix"
          backend {
            service {
              name = kubernetes_service_v1.frontend.metadata[0].name
              port {
                number = 80
              }
            }
          }
        }

        path {
          path      = "/health"
          path_type = "Prefix"
          backend {
            service {
              name = kubernetes_service_v1.backend.metadata[0].name
              port {
                number = 8000
              }
            }
          }
        }
      }
    }
  }
}
