provider "kubernetes" {
  config_path    = var.kubeconfig_path
  config_context = var.kube_context
}

module "extensionsite_app" {
  source = "./extensionsite_app"

  namespace                = var.namespace
  node_name                = var.node_name
  preserved_database_path  = var.preserved_database_path
  kubernetes_database_path = var.kubernetes_database_path
  volume_capacity          = var.volume_capacity
  runtime_secret_data      = var.runtime_secret_data
  backend_image            = var.backend_image
  frontend_image           = var.frontend_image
  migration_job_name       = var.migration_job_name
  postgres_image           = var.postgres_image
  redis_image              = var.redis_image
  mitmproxy_image          = var.mitmproxy_image
}
