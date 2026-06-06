# GitHub Environments Terraform

This Terraform stack manages repository environments for
`Lipford-Dutch/nautobot-app-custom-metrics`.

## Managed Environments

- `development`
    - Branches: `develop`, `feature/*`, `bugfix/*`
    - No wait timer
    - No mandatory reviewers
- `staging`
    - Branches: `main`, `release/*`
    - Requires the QA leads team reviewer
    - No wait timer
- `production`
    - Branch: `main`
    - Tags: `v*.*.*`
    - Requires SRE approvers and CAB reviewer teams
    - Uses a 10-minute wait timer

## Apply Workflow

```powershell
terraform init
terraform plan -var-file="terraform.tfvars"
terraform apply -var-file="terraform.tfvars"
```

## Security Notes

- Do not commit `terraform.tfvars`, state files, or real secret values.
- Use environment-specific cloud roles and credentials.
- Keep production deploys tied to immutable semantic-version tags where possible.
- Reviewers are referenced by numeric GitHub team IDs, not display names.
