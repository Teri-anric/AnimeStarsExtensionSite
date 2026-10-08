variable "namespace" {
  type        = string
  description = "Namespace owned by AnimeStarsExtensionSite."
}

variable "node_name" {
  type        = string
  description = "Node hosting the site's local PostgreSQL directories and workloads."
}

variable "preserved_database_path" {
  type        = string
  description = "Preserved original PostgreSQL data path on the selected node."
}

variable "kubernetes_database_path" {
  type        = string
  description = "Active PostgreSQL data path on the selected node."
}

variable "volume_capacity" {
  type        = string
  description = "Kubernetes capacity metadata for the static local PVs."
}

variable "runtime_secret_data" {
  type        = map(string)
  description = "Runtime Secret values; stored in Terraform state."
  sensitive   = true
}

variable "backend_image" {
  type        = string
  description = "Immutable backend image reference used by backend, scheduler, and migrations."
}

variable "frontend_image" {
  type        = string
  description = "Immutable frontend image reference."
}

variable "migration_job_name" {
  type        = string
  description = "Unique name for the release migration Job."
}

variable "postgres_image" {
  type        = string
  description = "PostgreSQL image used by the database and migration wait container."
}

variable "redis_image" {
  type        = string
  description = "Redis image used by the disposable application queue."
}

variable "mitmproxy_image" {
  type        = string
  description = "mitmproxy image used by the application parser."
}
