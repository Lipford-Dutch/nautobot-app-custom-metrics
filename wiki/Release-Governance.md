# Release Governance

## Current Approval Model

The repository owner approved Production v1.0.0 promotion on August 29, 2026
after acceptance testing passed. Future production releases remain subject to
reviewed release PRs and required repository checks.

## Required Production Governance

- Protected `main` and `develop` branches
- Required CI checks
- Code-owner review for stable release promotion
- GitHub environments for development, staging, and production
- Dedicated QA, SRE, and CAB reviewers
- Secret scanning and push protection
- Dependency advisory disposition

## Release Promotion

- Prereleases are published from the active integration branch.
- Stable production releases are promoted through a reviewed release PR.
- Release artifacts must include wheel, sdist, checksums, and provenance.
