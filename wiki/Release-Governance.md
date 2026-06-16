# Release Governance

## Current Approval Model

The repository owner granted blanket approval on 2026-06-16 for Alpha and
release-candidate evidence while formal QA, SRE, and CAB teams are still being
created.

This approval supports Alpha and release-candidate publication. It does not
replace production separation of duties.

## Required Production Governance

- Protected `main` and `develop` branches
- Required CI checks
- Code-owner review for stable release promotion
- GitHub environments for development, staging, and production
- Dedicated QA, SRE, and CAB reviewers
- Secret scanning and push protection
- Dependency advisory disposition

## Release Promotion

- Alpha and RC releases are published from `develop`.
- Stable production releases are promoted through a reviewed release PR.
- Release artifacts must include wheel, sdist, checksums, and provenance.

