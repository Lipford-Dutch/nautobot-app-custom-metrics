variable "github_owner" {
  description = "GitHub organization or owner that contains the target repository."
  type        = string
}

variable "repository_name" {
  description = "Target GitHub repository name without the owner prefix."
  type        = string
}

variable "team_qa_leads_id" {
  description = "Numeric GitHub team ID for staging deployment reviewers."
  type        = number
}

variable "team_sre_approvers_id" {
  description = "Numeric GitHub team ID for production SRE deployment approvers."
  type        = number
}

variable "team_cab_id" {
  description = "Numeric GitHub team ID for production change advisory board approvers."
  type        = number
}

variable "development_aws_role_arn" {
  description = "Development AWS OIDC role ARN. Use least privilege and environment-specific trust conditions."
  type        = string
  sensitive   = true
}

variable "staging_aws_role_arn" {
  description = "Staging AWS OIDC role ARN. Must not be reused from other environments."
  type        = string
  sensitive   = true
}

variable "production_aws_role_arn" {
  description = "Production AWS OIDC role ARN. Must not be reused from other environments."
  type        = string
  sensitive   = true
}

variable "staging_external_service_token" {
  description = "Placeholder staging-only external service credential."
  type        = string
  sensitive   = true
}

variable "production_external_service_token" {
  description = "Placeholder production-only external service credential."
  type        = string
  sensitive   = true
}
