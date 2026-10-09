# Both public hosts enter through the cluster-wide KEDA HTTP interceptor.
# Traefik keeps TLS termination and forwards the original Host header so the
# interceptor can select the matching InterceptorRoute.
resource "kubernetes_service_v1" "keda_http" {
  metadata {
    name      = "keda-http"
    namespace = kubernetes_namespace_v1.site.metadata[0].name
    labels    = local.common_labels
  }

  spec {
    type          = "ExternalName"
    external_name = "keda-add-ons-http-interceptor-proxy.keda.svc.cluster.local"

    port {
      name        = "http"
      port        = 8080
      target_port = 8080
    }
  }
}

resource "kubernetes_manifest" "frontend_interceptor_route" {
  manifest = {
    apiVersion = "http.keda.sh/v1beta1"
    kind       = "InterceptorRoute"
    metadata = {
      name      = "frontend"
      namespace = kubernetes_namespace_v1.site.metadata[0].name
      labels    = local.labels.frontend
    }
    spec = {
      target = {
        service = kubernetes_service_v1.frontend.metadata[0].name
        port    = 8080
      }
      rules = [{
        hosts = ["ass.strawberrycat.dev"]
      }]
      scalingMetric = {
        concurrency = { targetValue = 100 }
      }
      coldStart = {
        maxPendingRequests = 100
        overflow           = "Reject"
      }
      timeouts = {
        readiness = "120s"
        request   = "0s"
      }
    }
  }

}

resource "kubernetes_manifest" "frontend_scaled_object" {
  manifest = {
    apiVersion = "keda.sh/v1alpha1"
    kind       = "ScaledObject"
    metadata = {
      name      = "frontend"
      namespace = kubernetes_namespace_v1.site.metadata[0].name
      labels    = local.labels.frontend
    }
    spec = {
      scaleTargetRef = {
        name       = "frontend"
        kind       = "Deployment"
        apiVersion = "apps/v1"
      }
      minReplicaCount = 0
      maxReplicaCount = 2
      cooldownPeriod  = 300
      triggers = [{
        type = "external-push"
        metadata = {
          scalerAddress    = "keda-add-ons-http-external-scaler.keda:9090"
          interceptorRoute = kubernetes_manifest.frontend_interceptor_route.manifest.metadata.name
        }
      }]
    }
  }

  depends_on = [kubernetes_manifest.frontend_interceptor_route]
}

resource "kubernetes_manifest" "backend_interceptor_route" {
  manifest = {
    apiVersion = "http.keda.sh/v1beta1"
    kind       = "InterceptorRoute"
    metadata = {
      name      = "backend"
      namespace = kubernetes_namespace_v1.site.metadata[0].name
      labels    = local.labels.backend
    }
    spec = {
      target = {
        service = kubernetes_service_v1.backend.metadata[0].name
        port    = 8000
      }
      rules = [{
        hosts = ["ass-api.strawberrycat.dev"]
      }]
      scalingMetric = {
        concurrency = { targetValue = 100 }
      }
      coldStart = {
        maxPendingRequests = 100
        overflow           = "Reject"
      }
      timeouts = {
        readiness = "300s"
        request   = "0s"
      }
    }
  }

}

resource "kubernetes_manifest" "backend_scaled_object" {
  manifest = {
    apiVersion = "keda.sh/v1alpha1"
    kind       = "ScaledObject"
    metadata = {
      name      = "backend"
      namespace = kubernetes_namespace_v1.site.metadata[0].name
      labels    = local.labels.backend
    }
    spec = {
      scaleTargetRef = {
        name       = "backend"
        kind       = "Deployment"
        apiVersion = "apps/v1"
      }
      minReplicaCount = 0
      maxReplicaCount = 3
      cooldownPeriod  = 300
      triggers = [{
        type = "external-push"
        metadata = {
          scalerAddress    = "keda-add-ons-http-external-scaler.keda:9090"
          interceptorRoute = kubernetes_manifest.backend_interceptor_route.manifest.metadata.name
        }
      }]
    }
  }

  depends_on = [kubernetes_manifest.backend_interceptor_route]
}
