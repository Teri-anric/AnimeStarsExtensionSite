variable "kubeconfig_path" {
  type        = string
  description = "Path to kubeconfig for the prod k3s cluster."
}

variable "kube_context" {
  type        = string
  description = "kubectl context name for prod."
  default     = "k3s"
}

variable "namespace" {
  type        = string
  description = "Namespace for prod."
  default     = "animestars-prod"
}

variable "host" {
  type        = string
  description = "Prod ingress host."
  default     = "ass.strawberrycat.dev"
}

variable "ingress_class" {
  type        = string
  description = "Ingress class name (k3s default is traefik)."
  default     = "traefik"
}

variable "backend_image" {
  type        = string
  description = "Backend image repository (no tag)."
  default     = "localhost:5000/animestars/backend"
}

variable "frontend_image" {
  type        = string
  description = "Frontend image repository (no tag)."
  default     = "localhost:5000/animestars/frontend"
}

variable "backend_tag" {
  type        = string
  description = "Backend image tag for prod."
  default     = "prod"
}

variable "frontend_tag" {
  type        = string
  description = "Frontend image tag for prod."
  default     = "prod"
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
  default     = "socks5://proxy:8080"
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
  default     = true
}

variable "proxy_image" {
  type        = string
  description = "Proxy image."
  default     = "mitmproxy/mitmproxy:latest"
}

variable "traefik_certresolver" {
  type        = string
  description = "Traefik certResolver name."
  default     = "le"
}
