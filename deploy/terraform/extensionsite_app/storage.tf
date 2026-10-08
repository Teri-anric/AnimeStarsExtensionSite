resource "kubernetes_persistent_volume_v1" "preserved_postgres" {
  # Kubernetes fills the binding reference after the PVC is bound.
  lifecycle {
    ignore_changes = [spec[0].claim_ref]
  }

  metadata {
    name   = "animestars-extension-site-postgres-s0"
    labels = merge(local.common_labels, { "app.kubernetes.io/name" = "animestars-extension-site-postgres" })
  }

  spec {
    capacity = { storage = var.volume_capacity }

    access_modes                     = ["ReadWriteOnce"]
    volume_mode                      = "Filesystem"
    persistent_volume_reclaim_policy = "Retain"
    storage_class_name               = ""

    persistent_volume_source {
      local { path = var.preserved_database_path }
    }

    node_affinity {
      required {
        node_selector_term {
          match_expressions {
            key      = "kubernetes.io/hostname"
            operator = "In"
            values   = [var.node_name]
          }
        }
      }
    }

    claim_ref {
      namespace = var.namespace
      name      = "postgres-data"
    }
  }
}

resource "kubernetes_persistent_volume_claim_v1" "preserved_postgres" {
  metadata {
    name      = "postgres-data"
    namespace = kubernetes_namespace_v1.site.metadata[0].name
    labels    = merge(local.common_labels, { "app.kubernetes.io/name" = "animestars-extension-site-postgres" })
  }

  spec {
    access_modes       = ["ReadWriteOnce"]
    storage_class_name = ""
    volume_name        = kubernetes_persistent_volume_v1.preserved_postgres.metadata[0].name

    resources { requests = { storage = var.volume_capacity } }

    selector {
      match_labels = { "app.kubernetes.io/name" = "animestars-extension-site-postgres" }
    }
  }
}

resource "kubernetes_persistent_volume_v1" "active_postgres" {
  # Kubernetes fills the binding reference after the PVC is bound.
  lifecycle {
    ignore_changes = [spec[0].claim_ref]
  }

  metadata {
    name   = "animestars-extension-site-postgres-restore-s0"
    labels = merge(local.common_labels, { "app.kubernetes.io/name" = "animestars-extension-site-postgres" })
  }

  spec {
    capacity = { storage = var.volume_capacity }

    access_modes                     = ["ReadWriteOnce"]
    volume_mode                      = "Filesystem"
    persistent_volume_reclaim_policy = "Retain"
    storage_class_name               = ""

    persistent_volume_source {
      local { path = var.kubernetes_database_path }
    }

    node_affinity {
      required {
        node_selector_term {
          match_expressions {
            key      = "kubernetes.io/hostname"
            operator = "In"
            values   = [var.node_name]
          }
        }
      }
    }

    claim_ref {
      namespace = var.namespace
      name      = "postgres-restore-data"
    }
  }
}

resource "kubernetes_persistent_volume_claim_v1" "active_postgres" {
  metadata {
    name      = "postgres-restore-data"
    namespace = kubernetes_namespace_v1.site.metadata[0].name
    labels    = merge(local.common_labels, { "app.kubernetes.io/name" = "animestars-extension-site-postgres" })
  }

  spec {
    access_modes       = ["ReadWriteOnce"]
    storage_class_name = ""
    volume_name        = kubernetes_persistent_volume_v1.active_postgres.metadata[0].name

    resources { requests = { storage = var.volume_capacity } }

    selector {
      match_labels = { "app.kubernetes.io/name" = "animestars-extension-site-postgres" }
    }
  }
}
