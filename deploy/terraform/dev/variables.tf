variable "kubeconfig_path" {
  type        = string
  description = "Path to kubeconfig for the dev Kind cluster."
}

variable "kube_context" {
  type        = string
  description = "kubectl context name for dev."
  default     = "kind-animestars-dev"
}

variable "namespace" {
  type        = string
  description = "Namespace for dev."
  default     = "animestars-dev"
}

variable "host" {
  type        = string
  description = "Dev ingress host."
  default     = "animestars.local"
}

variable "ingress_class" {
  type        = string
  description = "Ingress class name."
  default     = "traefik"
}

variable "backend_image" {
  type        = string
  description = "Backend image repository (no tag)."
  default     = "animestars/backend"
}

variable "frontend_image" {
  type        = string
  description = "Frontend image repository (no tag)."
  default     = "animestars/frontend"
}

variable "backend_tag" {
  type        = string
  description = "Backend image tag for dev."
  default     = "dev"
}

variable "frontend_tag" {
  type        = string
  description = "Frontend image tag for dev."
  default     = "dev"
}

variable "postgres_password" {
  type        = string
  description = "Postgres password (stored in TF state)."
  sensitive   = true
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
  description = "Deploy the scheduler (uses backend image)."
  default     = true
}

variable "enable_proxy" {
  type        = bool
  description = "Deploy a socks5 proxy service (mitmproxy) inside the namespace."
  default     = false
}

variable "proxy_image" {
  type        = string
  description = "Proxy image."
  default     = "mitmproxy/mitmproxy:latest"
}

variable "install_traefik" {
  type        = bool
  description = "Install a minimal Traefik ingress controller into Kind."
  default     = true
}

variable "traefik_namespace" {
  type        = string
  description = "Namespace for Traefik."
  default     = "traefik"
}

variable "traefik_image" {
  type        = string
  description = "Traefik image for Kind."
  default     = "traefik:v2.11.16"
}
