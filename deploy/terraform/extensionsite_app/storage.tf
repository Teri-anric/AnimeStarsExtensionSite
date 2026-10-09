# K3s local-path provisions and manages the node-local directory for this
# database. Terraform intentionally does not provide a host filesystem path.
resource "kubernetes_storage_class_v1" "postgres_retained" {
  metadata {
    name = "animestars-postgres-retain"
    labels = merge(local.common_labels, {
      "app.kubernetes.io/name" = "postgres"
    })
  }

  storage_provisioner    = "rancher.io/local-path"
  reclaim_policy         = "Retain"
  volume_binding_mode    = "WaitForFirstConsumer"
  allow_volume_expansion = true
}

resource "kubernetes_persistent_volume_claim_v1" "migration_target_postgres" {
  wait_until_bound = false

  metadata {
    name      = "postgres-migration-target-data"
    namespace = kubernetes_namespace_v1.site.metadata[0].name
    labels    = merge(local.common_labels, { "app.kubernetes.io/name" = "postgres-migration-target" })
  }

  spec {
    access_modes       = ["ReadWriteOnce"]
    storage_class_name = kubernetes_storage_class_v1.postgres_retained.metadata[0].name

    resources { requests = { storage = var.volume_capacity } }
  }

  lifecycle {
    # Preserve the migrated database during any app-level Terraform destroy.
    prevent_destroy = true
  }
}
