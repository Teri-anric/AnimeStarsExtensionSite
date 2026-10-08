# Traefik is installed and managed by infra-s1. This resource owns only the
# project's route object inside its existing CRD API.
resource "kubernetes_manifest" "site_ingress_route" {
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
            name = kubernetes_service_v1.frontend.metadata[0].name
            port = 8080
          }]
        },
        {
          match = "Host(`ass-api.strawberrycat.dev`)"
          kind  = "Rule"
          services = [{
            name = kubernetes_service_v1.backend.metadata[0].name
            port = 8000
          }]
        },
      ]
      tls = { certResolver = "le" }
    }
  }

  depends_on = [
    kubernetes_deployment_v1.backend,
    kubernetes_deployment_v1.frontend,
    kubernetes_deployment_v1.scheduler,
  ]
}
