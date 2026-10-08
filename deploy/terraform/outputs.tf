output "namespace" {
  description = "Application namespace managed by this Terraform root."
  value       = module.extensionsite_app.namespace
}

output "postgres_paths" {
  description = "Local PostgreSQL paths retained on the s0 node."
  value = {
    preserved = var.preserved_database_path
    active    = var.kubernetes_database_path
  }
}
