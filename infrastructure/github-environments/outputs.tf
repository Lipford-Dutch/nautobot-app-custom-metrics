output "environment_names" {
  description = "GitHub Environments managed by this Terraform configuration."
  value = [
    github_repository_environment.development.environment,
    github_repository_environment.staging.environment,
    github_repository_environment.production.environment,
  ]
}

output "deployment_policy_summary" {
  description = "Human-readable summary of branch and tag policy boundaries."
  value = {
    development = "Branches: develop, feature/*, bugfix/*"
    staging     = "Branches: main, release/*; reviewer: QA leads"
    production  = "Branch: main; tags: v*.*.*; reviewers: SRE approvers and CAB; wait timer: 10 minutes"
  }
}
