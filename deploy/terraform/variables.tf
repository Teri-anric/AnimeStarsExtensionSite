variable "kubeconfig_path" {
  type        = string
  description = "Path to the authorized kubeconfig for the existing s1 K3s cluster."
  default     = "~/.kube/k3s-s1.yaml"
}

variable "kube_context" {
  type        = string
  description = "Context for the existing K3s cluster containing s1 and s0."
  default     = "k3s"
}

variable "namespace" {
  type        = string
  description = "Namespace owned by AnimeStarsExtensionSite."
  default     = "animestars-extension-site"
}

variable "node_name" {
  type        = string
  description = "Kubernetes node hosting this project's local PostgreSQL directories."
  default     = "s0.teri"
}

variable "preserved_database_path" {
  type        = string
  description = "Preserved original PostgreSQL data path on the selected node."
  default     = "/root/Teri-anric/AnimeStarsExtensionSite/db"
}

variable "kubernetes_database_path" {
  type        = string
  description = "Active PostgreSQL data path on the selected node."
  default     = "/root/Teri-anric/AnimeStarsExtensionSite/db-k8s"
}

variable "volume_capacity" {
  type        = string
  description = "Kubernetes capacity metadata; does not resize host filesystems."
  default     = "10Gi"
}

variable "runtime_secret_data" {
  type        = map(string)
  description = "Sensitive values for the app runtime Secret; stored in Terraform state."
  sensitive   = true
}

variable "backend_image" {
  type        = string
  description = "Immutable backend image reference, also used by scheduler and migrations."
  default     = "localhost:5000/animestars-extensionsite-backend:migration-20261008-greenlet01"
}

variable "frontend_image" {
  type        = string
  description = "Immutable frontend image reference."
  default     = "localhost:5000/animestars-extensionsite-frontend:migration-20261008-01a11c7f"
}

variable "migration_job_name" {
  type        = string
  description = "Unique name for the release migration Job."
  default     = "animestars-extension-site-alembic-upgrade"
}

variable "postgres_image" {
  type        = string
  description = "PostgreSQL image used by the database and migration wait container."
  default     = "postgres:16"
}

variable "redis_image" {
  type        = string
  description = "Redis image used by the disposable application queue."
  default     = "redis:7-alpine"
}

variable "mitmproxy_image" {
  type        = string
  description = "mitmproxy image used by the application parser."
  default     = "mitmproxy/mitmproxy:11.0.2"
}
