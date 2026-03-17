terraform {
  required_version = ">= 1.5.0"

  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = ">= 2.20.0"
    }
  }
}

resource "kubernetes_namespace_v1" "traefik" {
  metadata {
    name = var.namespace
  }
}

resource "kubernetes_ingress_class_v1" "traefik" {
  metadata {
    name = var.ingress_class_name
  }

  spec {
    controller = "traefik.io/ingress-controller"
  }
}

resource "kubernetes_service_account_v1" "traefik" {
  metadata {
    name      = "traefik"
    namespace = kubernetes_namespace_v1.traefik.metadata[0].name
  }
}

resource "kubernetes_cluster_role_v1" "traefik" {
  metadata {
    name = "traefik"
  }

  rule {
    api_groups = [""]
    resources  = ["services", "endpoints", "secrets", "configmaps"]
    verbs      = ["get", "list", "watch"]
  }

  rule {
    api_groups = [""]
    resources  = ["nodes"]
    verbs      = ["get", "list", "watch"]
  }

  rule {
    api_groups = [""]
    resources  = ["pods"]
    verbs      = ["get", "list", "watch"]
  }

  rule {
    api_groups = ["networking.k8s.io"]
    resources  = ["ingresses", "ingressclasses", "ingresses/status"]
    verbs      = ["get", "list", "watch", "update"]
  }
}

resource "kubernetes_cluster_role_binding_v1" "traefik" {
  metadata {
    name = "traefik"
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = kubernetes_cluster_role_v1.traefik.metadata[0].name
  }

  subject {
    kind      = "ServiceAccount"
    name      = kubernetes_service_account_v1.traefik.metadata[0].name
    namespace = kubernetes_namespace_v1.traefik.metadata[0].name
  }
}

resource "kubernetes_daemon_set_v1" "traefik" {
  metadata {
    name      = "traefik"
    namespace = kubernetes_namespace_v1.traefik.metadata[0].name
    labels = {
      "app.kubernetes.io/name" = "traefik"
    }
  }

  spec {
    selector {
      match_labels = {
        "app.kubernetes.io/name" = "traefik"
      }
    }

    template {
      metadata {
        labels = {
          "app.kubernetes.io/name" = "traefik"
        }
      }

      spec {
        service_account_name = kubernetes_service_account_v1.traefik.metadata[0].name

        container {
          name  = "traefik"
          image = var.image

          args = [
            "--providers.kubernetesingress=true",
            "--providers.kubernetesingress.ingressclass=${var.ingress_class_name}",
            "--entrypoints.web.address=:80",
            "--entrypoints.websecure.address=:443",
            "--ping=true",
            "--ping.entrypoint=web",
            "--accesslog=true",
            "--log.level=INFO",
          ]

          port {
            name           = "web"
            container_port = 80
            host_port      = 80
          }

          port {
            name           = "websecure"
            container_port = 443
            host_port      = 443
          }

          security_context {
            allow_privilege_escalation = false
            capabilities {
              drop = ["ALL"]
            }
          }

          readiness_probe {
            http_get {
              path = "/ping"
              port = 80
            }
            period_seconds        = 5
            initial_delay_seconds = 5
          }

          liveness_probe {
            http_get {
              path = "/ping"
              port = 80
            }
            period_seconds        = 10
            initial_delay_seconds = 10
          }
        }

        node_selector = {
          "ingress-ready" = "true"
        }
      }
    }
  }
}
