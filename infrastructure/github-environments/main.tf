terraform {
  required_version = ">= 1.6.0"

  required_providers {
    github = {
      source  = "integrations/github"
      version = "~> 6.7"
    }
  }
}

provider "github" {
  owner = var.github_owner
}

locals {
  repository = var.repository_name

  development_deployment_policies = {
    develop = {
      pattern = "develop"
      type    = "branch"
    }
    feature = {
      pattern = "feature/*"
      type    = "branch"
    }
    bugfix = {
      pattern = "bugfix/*"
      type    = "branch"
    }
  }

  staging_deployment_policies = {
    main = {
      pattern = "main"
      type    = "branch"
    }
    release = {
      pattern = "release/*"
      type    = "branch"
    }
  }

  production_deployment_policies = {
    main = {
      pattern = "main"
      type    = "branch"
    }
    semver_tag = {
      pattern = "v*.*.*"
      type    = "tag"
    }
  }
}

resource "github_repository_environment" "development" {
  repository  = local.repository
  environment = "development"

  # SRE Standard: Development deploys should stay fast to preserve short feedback loops.
  wait_timer = 0

  # Security Standard: Admin bypass is disabled so privileged users cannot silently skip policy.
  can_admins_bypass = false

  deployment_branch_policy {
    # Zero Trust: Only explicitly listed branches can target this environment.
    protected_branches     = false
    custom_branch_policies = true
  }
}

resource "github_repository_environment_deployment_policy" "development" {
  for_each = local.development_deployment_policies

  repository     = local.repository
  environment    = github_repository_environment.development.environment
  branch_pattern = each.value.pattern
}

resource "github_actions_environment_variable" "development_tf_var_env" {
  repository    = local.repository
  environment   = github_repository_environment.development.environment
  variable_name = "TF_VAR_env"
  value         = "development"
}

resource "github_actions_environment_secret" "development_aws_role_arn" {
  repository      = local.repository
  environment     = github_repository_environment.development.environment
  secret_name     = "AWS_ROLE_ARN"
  plaintext_value = var.development_aws_role_arn

  # Security Standard: Use an environment-scoped OIDC role instead of a shared repository secret.
}

resource "github_repository_environment" "staging" {
  repository  = local.repository
  environment = "staging"

  # SRE Standard: Staging has human approval but no artificial deployment delay.
  wait_timer = 0

  # Security Standard: Prevent deploy initiators from approving their own promotion.
  prevent_self_review = true
  can_admins_bypass   = false

  reviewers {
    # SRE Standard: Require pre-production validation by a designated QA ownership group.
    teams = [var.team_qa_leads_id]
  }

  deployment_branch_policy {
    # Zero Trust: Staging accepts only release branches and main.
    protected_branches     = false
    custom_branch_policies = true
  }
}

resource "github_repository_environment_deployment_policy" "staging" {
  for_each = local.staging_deployment_policies

  repository     = local.repository
  environment    = github_repository_environment.staging.environment
  branch_pattern = each.value.type == "branch" ? each.value.pattern : null
  tag_pattern    = each.value.type == "tag" ? each.value.pattern : null
}

resource "github_actions_environment_variable" "staging_tf_var_env" {
  repository    = local.repository
  environment   = github_repository_environment.staging.environment
  variable_name = "TF_VAR_env"
  value         = "staging"
}

resource "github_actions_environment_secret" "staging_aws_role_arn" {
  repository      = local.repository
  environment     = github_repository_environment.staging.environment
  secret_name     = "AWS_ROLE_ARN"
  plaintext_value = var.staging_aws_role_arn

  # Security Standard: Staging uses a separate role to prevent privilege bleed between environments.
}

resource "github_actions_environment_secret" "staging_external_service_token" {
  repository      = local.repository
  environment     = github_repository_environment.staging.environment
  secret_name     = "STAGING_EXTERNAL_SERVICE_TOKEN"
  plaintext_value = var.staging_external_service_token

  # Security Standard: Credential names are environment-specific to prevent accidental reuse.
}

resource "github_repository_environment" "production" {
  repository  = local.repository
  environment = "production"

  # SRE Standard: Ten-minute hold allows sanity checks, monitoring observation, and emergency abort.
  wait_timer = 10

  # Security Standard: Live workloads require independent approval and no admin bypass.
  prevent_self_review = true
  can_admins_bypass   = false

  reviewers {
    # SRE Standard: Production requires independent approval from SRE and CAB owners.
    teams = [
      var.team_sre_approvers_id,
      var.team_cab_id,
    ]
  }

  deployment_branch_policy {
    # SRE Standard: Production is limited to main and immutable semantic-version tags.
    protected_branches     = false
    custom_branch_policies = true
  }
}

resource "github_repository_environment_deployment_policy" "production" {
  for_each = local.production_deployment_policies

  repository     = local.repository
  environment    = github_repository_environment.production.environment
  branch_pattern = each.value.type == "branch" ? each.value.pattern : null
  tag_pattern    = each.value.type == "tag" ? each.value.pattern : null
}

resource "github_actions_environment_variable" "production_tf_var_env" {
  repository    = local.repository
  environment   = github_repository_environment.production.environment
  variable_name = "TF_VAR_env"
  value         = "production"
}

resource "github_actions_environment_secret" "production_aws_role_arn" {
  repository      = local.repository
  environment     = github_repository_environment.production.environment
  secret_name     = "AWS_ROLE_ARN"
  plaintext_value = var.production_aws_role_arn

  # Security Standard: Production uses its own deployment identity scoped to live workloads only.
}

resource "github_actions_environment_secret" "production_external_service_token" {
  repository      = local.repository
  environment     = github_repository_environment.production.environment
  secret_name     = "PRODUCTION_EXTERNAL_SERVICE_TOKEN"
  plaintext_value = var.production_external_service_token

  # Security Standard: Production credentials are not reused across lower environments.
}
