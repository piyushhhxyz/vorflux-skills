# Conventional Commit Types Reference

Used by Angular, React, Vue, Nx, Turborepo, and most major OSS projects.

## Types

| Type       | Use when...                                                          | Bumps version? |
|------------|----------------------------------------------------------------------|----------------|
| `feat`     | A new feature is added                                               | Minor          |
| `fix`      | A bug is fixed                                                       | Patch          |
| `refactor` | Code restructured without behavior change                            | None           |
| `perf`     | Performance improvement                                              | Patch          |
| `docs`     | Documentation only (README, JSDoc, comments)                         | None           |
| `test`     | Adding or fixing tests                                               | None           |
| `chore`    | Build system, deps, tooling, CI config                               | None           |
| `ci`       | CI/CD pipeline changes                                               | None           |
| `style`    | Formatting, whitespace, linting (no logic change)                    | None           |
| `revert`   | Reverting a previous commit                                          | Patch          |
| `build`    | Build system or external dependency changes                          | None           |

## Scopes (examples)

Use the module, package, or area most affected:
- `auth`, `api`, `ui`, `db`, `config`, `deps`, `cli`, `tests`

## Breaking changes

Add `!` after type/scope **and** a footer:

```
feat(api)!: remove deprecated /v1/users endpoint

BREAKING CHANGE: /v1/users is removed. Migrate to /v2/users.
```

## Examples

```
feat(auth): add OAuth2 Google login
fix(db): resolve connection pool exhaustion under high load
refactor(api): extract response serializer into separate module
chore(deps): bump axios from 1.3.4 to 1.6.8
docs(readme): add deployment instructions for Railway
test(auth): add unit tests for JWT expiry edge cases
ci(github-actions): add Node 20 to test matrix
perf(search): add composite index on (name, category) columns
```
