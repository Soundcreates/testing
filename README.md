# Kubeflow Testing

This repository hosts shared CI building blocks for the Kubeflow community: reusable GitHub Actions
and scripts that any Kubeflow Subproject can consume from its own `.github/workflows` or `Makefile`.
The goal is to reduce duplication across Kubeflow repositories and to give the maintainers one place
to align on CI best practices.

## Common Scripts

The following scripts are available.

### Checking license headers

Every source file needs the Apache 2.0 header from `hack/boilerplate/`. New files must use the
year-less header (`Copyright The Kubeflow Authors.`). The verifier rejects a hardcoded year on
files added relative to the base branch.

Run this script as follows:

```bash
python hack/boilerplate/boilerplate.py --base-ref master
```

Vendored third-party code that must keep its upstream license header can be skipped with
`--exclude`, which takes a Python regular expression matched (with `re.search`) against each
file's repository-relative path. Repeat the flag for multiple patterns:

```bash
python hack/boilerplate/boilerplate.py --base-ref main \
  --exclude '^third_party/' \
  --exclude '^internal/starrocks/mysqldriver/'
```

## Common GitHub Actions

The following GitHub actions are available.

### PR admission gate

Gates pull requests from external contributors on a maintainer-triaged issue. Kubeflow organization
members bypass the issue check. Other authors must reference an issue in the calling repository with
`Fixes #123` at the start of its own line, and that issue must have the configured admission label.
Admitted pull requests receive `ok-to-test`; `needs-ok-to-test` is removed and pending fork workflow
runs for the current head are approved. Pull requests that do not meet the policy receive an
explanation and are closed.

Create a caller such as `.github/workflows/pr-admission.yml`. Pin the reusable workflow to a full
commit SHA, and create the `ok-to-test`, `needs-ok-to-test`, and admission labels in the calling
repository before enabling it:

```yaml
name: PR Admission

on:
  pull_request_target:
    types: [opened, labeled, synchronize, reopened]

permissions:
  actions: write
  contents: read
  pull-requests: write
  issues: read

jobs:
  admission:
    uses: kubeflow/testing/.github/workflows/pr-admission-gate.yml@<commit-sha>
    with:
      admission_label: ready
      exempt_bots: '["dependabot[bot]", "copybara-service[bot]"]'
```

The gate checks out only its helper scripts from the pinned `kubeflow/testing` commit. It never
checks out or executes code from the pull request. The caller cannot grant the reusable workflow
more permissions than those declared above. An invalid bot JSON value, unavailable membership data,
or ambiguous pull-request head fails closed without approving workflow runs.

### verify-boilerplate

Runs the license header check above against the calling repository. Check out the repository
with `fetch-depth: 0` first so the base branch can be resolved:

```yaml
- uses: actions/checkout@v5
  with:
    fetch-depth: 0
- uses: kubeflow/testing/.github/actions/verify-boilerplate@<commit-sha>
  with:
    base-ref: main
    # Optional: one regular expression per line; blank lines and # comments are ignored.
    exclude: |
      ^third_party/
      # Vendored go-sql-driver/mysql (MPL-2.0); keeps its upstream header.
      ^internal/starrocks/mysqldriver/
```

## Contributing

We welcome contributions to enhance support for common Kubeflow infrastructure! Please see our
[CONTRIBUTING guide](CONTRIBUTING.md) for details.
