# Security Advisory Disposition

This project tracks dependency and repository-control findings as release
gates. Findings must be fixed, upgraded away, or explicitly accepted before a
production release.

## Current Advisory Exceptions

| Finding | Source | Status | Production Requirement |
| --- | --- | --- | --- |
| `PyJWT==2.12.1` advisories | Inherited through Nautobot dependency constraints. | Upstream constrained. | Track Nautobot security releases and document risk acceptance until Nautobot permits a fixed dependency. |
| `pylint-nautobot 1.0.0` Python `<3.14` constraint | Development tooling only. | Accepted for CI tooling. | Keep runtime tests on Python 3.14 and run the Pylint/App Config stage on Python 3.13 until tooling supports Python 3.14. |

## Required Repository Controls

| Control | Required Setting |
| --- | --- |
| Default workflow token | Read-only. |
| Pull request approvals | Actions cannot approve pull requests. |
| Secret scanning | Enabled. |
| Push protection | Enabled. |
| Dependabot security updates | Enabled. |
| Main branch | Protected with required checks, code-owner review, stale-review dismissal, last-push approval, conversation resolution, and admin enforcement. |
| Develop branch | Protected with required checks, conversation resolution, and admin enforcement. |
| Deployment environments | `development`, `staging`, and `production` with environment-specific branch policies and secrets. |

## Exception Process

1. Record the advisory identifier, package, affected versions, and source.
2. Confirm whether the finding is runtime, development-only, or transitive.
3. Attempt an upgrade in a branch and run the full validation matrix.
4. If blocked by Nautobot or another upstream package, document the blocker and
   target upstream release.
5. Record compensating controls, such as limited exposure, authentication,
   branch protection, and dependency-review gates.
6. Revisit every accepted exception before each release.

## Release Gate

A production release cannot be approved while a high or critical advisory is
open unless the advisory has an explicit owner-approved exception and a review
date. Alpha prereleases may proceed with documented upstream-constrained
exceptions when the affected package cannot be upgraded independently without
breaking Nautobot compatibility.

