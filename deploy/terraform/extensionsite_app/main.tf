locals {
  common_labels = {
    "app.kubernetes.io/part-of" = "animestars-extension-site"
  }

  labels = {
    postgres  = merge(local.common_labels, { "app.kubernetes.io/name" = "postgres" })
    redis     = merge(local.common_labels, { "app.kubernetes.io/name" = "redis" })
    backend   = merge(local.common_labels, { "app.kubernetes.io/name" = "backend" })
    frontend  = merge(local.common_labels, { "app.kubernetes.io/name" = "frontend" })
    scheduler = merge(local.common_labels, { "app.kubernetes.io/name" = "scheduler" })
    mitmproxy = merge(local.common_labels, { "app.kubernetes.io/name" = "mitmproxy" })
  }
}

resource "kubernetes_namespace_v1" "site" {
  metadata {
    name   = var.namespace
    labels = local.common_labels
  }
}
