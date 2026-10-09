resource "kubernetes_config_map_v1" "domain_index_project" {
  metadata {
    name      = "domain-index-project"
    namespace = kubernetes_namespace_v1.site.metadata[0].name
    labels = {
      "strawberrycat.dev/domain-index" = "true"
    }
  }

  data = {
    "project.json" = jsonencode({
      id          = "animestars"
      name        = "AnimeStars"
      domain      = "ass.strawberrycat.dev"
      url         = "https://ass.strawberrycat.dev"
      description = "AnimeStars browser extension site."
      group       = "private"
      rank        = 2
    })
  }
}
