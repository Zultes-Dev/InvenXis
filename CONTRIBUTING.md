# Contributing to InvenXis

Thanks for your interest in contributing! Please take a moment to read this guide.

## Getting Started

1. Fork the repository and clone your fork.
2. Create a feature branch: `git checkout -b feat/your-feature`.
3. Set up the project by following the README's [Getting Started](README.md#getting-started).

## Commit Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` — a new feature
- `fix:` — a bug fix
- `docs:` — documentation only
- `refactor:` — code change that neither fixes a bug nor adds a feature
- `ci:` — CI configuration changes
- `chore:` — maintenance (deps, tooling, housekeeping)

Examples: `feat(api): add stock filter`, `fix(ui): correct dark-mode contrast`.

Use the imperative mood ("add", "fix", not "added"/"fixed").

## Development Workflow

1. Implement your change with tests (backend: `pytest`, frontend: `npm run build` /
   `npm run lint`).
2. Run the full test suite before opening a PR:

```bash
# Backend
pytest

# Frontend
cd frontend && npm run build && npm run lint
```

3. Push your branch and open a Pull Request.

## Pull Requests

- Keep PRs focused: one logical change per PR.
- Include a clear description and reference any related issue.
- Ensure CI passes.
- Update documentation (README, CHANGELOG) when user-facing behavior changes.

## Reporting Bugs / Requests

Use the provided issue templates:
- [Bug report](.github/ISSUE_TEMPLATE/bug_report.yml)
- [Feature request](.github/ISSUE_TEMPLATE/feature_request.yml)

By participating, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).