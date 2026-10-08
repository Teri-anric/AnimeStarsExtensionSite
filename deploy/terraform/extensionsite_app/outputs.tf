output "namespace" {
  description = "Application namespace managed by the app module."
  value       = kubernetes_namespace_v1.site.metadata[0].name
}
