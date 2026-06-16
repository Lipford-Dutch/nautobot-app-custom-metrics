# Project Wiki

The project wiki is source-controlled in `wiki/` and deployed to the GitHub
Wiki repository through GitHub Actions.

## Goals

- Provide a fast operational knowledge base for maintainers and reviewers.
- Mirror the GitHub Pages documentation style through the same content
  hierarchy, wording, and project navigation conventions.
- Keep wiki changes reviewed through pull requests.
- Avoid manual edits in the GitHub Wiki UI except for emergency notes that are
  later reconciled back into `wiki/`.

## Source Layout

| File | Purpose |
| --- | --- |
| `wiki/Home.md` | Wiki landing page and navigation hub. |
| `wiki/Project-Overview.md` | Current project state and v3 direction. |
| `wiki/V3-Roadmap.md` | v3 feature workstreams and final major revision policy. |
| `wiki/Collector-Architecture.md` | Collector design principles and planned adapters. |
| `wiki/Operations-Runbook.md` | Release-candidate and production-like validation runbook. |
| `wiki/Release-Governance.md` | Approval, environment, and release promotion policy. |
| `wiki/Bug-Fix-Workflow.md` | Bug-fix lane and release-blocking bug process. |

## Deployment

The `Deploy GitHub Wiki` workflow publishes `wiki/*.md` to the repository wiki
after changes merge to `develop` or when manually dispatched.

The workflow intentionally uses plain git commands with the GitHub token. This
keeps the deployment auditable and avoids unnecessary third-party deployment
actions.

## Style Guidance

- Keep pages concise and operational.
- Link back to the full GitHub Pages documentation for detailed procedures.
- Use the same terminology as the MkDocs site.
- Prefer tables and short runbooks over long prose.
- Do not publish secrets, tokens, customer names, or production-only topology.

