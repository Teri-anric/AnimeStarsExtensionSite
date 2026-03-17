variable "namespace" {
  type        = string
  description = "Target namespace for the app stack."
}

variable "host" {
  type        = string
  description = "Ingress host."
}

variable "ingress_class" {
  type        = string
  description = "Ingress class name."
  default     = "traefik"
}

variable "backend_image" {
  type        = string
  description = "Backend image repository (without tag)."
  default     = "animestars/backend"
}

variable "frontend_image" {
  type        = string
  description = "Frontend image repository (without tag)."
  default     = "animestars/frontend"
}

variable "backend_tag" {
  type        = string
  description = "Backend image tag."
}

variable "frontend_tag" {
  type        = string
  description = "Frontend image tag."
}

variable "postgres_password" {
  type        = string
  description = "Postgres password (stored in TF state)."
  sensitive   = true
}

variable "postgres_storage" {
  type        = string
  description = "PVC size for Postgres."
  default     = "1Gi"
}

variable "postgres_db" {
  type        = string
  description = "Postgres database name."
  default     = "animestars"
}

variable "postgres_user" {
  type        = string
  description = "Postgres user."
  default     = "animestars"
}

variable "parser_proxy" {
  type        = string
  description = "Optional proxy URL for the parser (e.g. socks5://proxy:8080)."
  default     = null
}

variable "parser_base_url" {
  type        = string
  description = "Optional base URL for the parser."
  default     = null
}

variable "enable_scheduler" {
  type        = bool
  description = "Deploy the scheduler as a separate Deployment (uses backend image)."
  default     = true
}

variable "enable_proxy" {
  type        = bool
  description = "Deploy a local socks5 proxy service (mitmproxy) inside the namespace."
  default     = false
}

variable "proxy_image" {
  type        = string
  description = "Proxy image."
  default     = "mitmproxy/mitmproxy:latest"
}

variable "enable_tls" {
  type        = bool
  description = "Enable TLS in Ingress via Traefik annotations (certResolver)."
  default     = false
}

variable "traefik_certresolver" {
  type        = string
  description = "Traefik certResolver name used for ACME."
  default     = "le"
}
