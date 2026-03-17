variable "namespace" {
  type        = string
  description = "Namespace to install Traefik into."
  default     = "traefik"
}

variable "ingress_class_name" {
  type        = string
  description = "IngressClass name to create."
  default     = "traefik"
}

variable "image" {
  type        = string
  description = "Traefik image."
  default     = "traefik:v2.11.16"
}

