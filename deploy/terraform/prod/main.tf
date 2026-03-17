terraform {
  required_version = ">= 1.5.0"

  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = ">= 2.20.0"
    }
  }
}

provider "kubernetes" {
  config_path    = var.kubeconfig_path
  config_context = var.kube_context
}

module "animestars" {
  source = "../modules/animestars_app"

  namespace            = var.namespace
  host                 = var.host
  ingress_class        = var.ingress_class
  enable_tls           = true
  traefik_certresolver = var.traefik_certresolver

  backend_image     = var.backend_image
  backend_tag       = var.backend_tag
  frontend_image    = var.frontend_image
  frontend_tag      = var.frontend_tag
  postgres_password = var.postgres_password
  postgres_db       = var.postgres_db
  postgres_user     = var.postgres_user
  parser_proxy      = var.parser_proxy
  parser_base_url   = var.parser_base_url
  enable_scheduler  = var.enable_scheduler
  enable_proxy      = var.enable_proxy
  proxy_image       = var.proxy_image
}
