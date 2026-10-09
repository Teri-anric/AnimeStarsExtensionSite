# Traefik is installed and managed by infra-s1. This resource owns only the
# project's route object inside its existing CRD API.
resource "kubernetes_manifest" "site_ingress_route" {
  field_manager {
    force_conflicts = true
  }

  manifest = {
    apiVersion = "traefik.io/v1alpha1"
    kind       = "IngressRoute"
    metadata = {
      name      = "animestars-extension-site"
      namespace = kubernetes_namespace_v1.site.metadata[0].name
      labels    = local.common_labels
    }
    spec = {
      entryPoints = ["websecure"]
      routes = [
        {
          match = "Host(`ass.strawberrycat.dev`)"
          kind  = "Rule"
          services = [{
            name = kubernetes_service_v1.keda_http.metadata[0].name
            port = 8080
          }]
        },
        {
          match = "Host(`ass-api.strawberrycat.dev`)"
          kind  = "Rule"
          services = [{
            name = kubernetes_service_v1.keda_http.metadata[0].name
            port = 8080
          }]
        },
      ]
      tls = { certResolver = "le" }
    }
  }

  depends_on = [
    kubernetes_manifest.backend_scaled_object,
    kubernetes_manifest.frontend_scaled_object,
  ]
}
