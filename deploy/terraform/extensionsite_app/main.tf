locals {
  common_labels = {
    "app.kubernetes.io/part-of" = "animestars-extension-site"
  }

  labels = {
    redis     = merge(local.common_labels, { "app.kubernetes.io/name" = "redis" })
    backend   = merge(local.common_labels, { "app.kubernetes.io/name" = "backend" })
    frontend  = merge(local.common_labels, { "app.kubernetes.io/name" = "frontend" })
    scheduler = merge(local.common_labels, { "app.kubernetes.io/name" = "scheduler" })
    mitmproxy = merge(local.common_labels, { "app.kubernetes.io/name" = "mitmproxy" })
  }

  runtime_config_data = {
    DATABASE__HOST  = "postgres-migration-target"
    DATABASE__PORT  = "5432"
    REDIS__HOST     = "redis"
    REDIS__PORT     = "6379"
    PARSER__PROXY   = "socks5://mitmproxy:8080"
    LOG_JSON        = "true"
    LOG_HTTP_BODIES = "false"
  }

  runtime_config_checksum_annotation = {
    "animestars.strawberrycat.dev/runtime-config-sha" = sha256(jsonencode(local.runtime_config_data))
  }
}

resource "kubernetes_namespace_v1" "site" {
  metadata {
    name   = var.namespace
    labels = local.common_labels
  }
}
