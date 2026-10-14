# CI onboarding checklist

Use this checklist when a new Kubeflow subproject sets up continuous integration.
Complete the steps in order so later jobs build on a reviewed and documented
baseline.

## 1. Establish ownership and review

- Add an `OWNERS` file with reviewers and approvers for the repository.
- Confirm the repository follows the
  [Kubeflow contribution guide](https://www.kubeflow.org/docs/about/contributing/)
  and the
  [Kubernetes code review process](https://git.k8s.io/community/contributors/guide/owners.md#the-code-review-process).
- Require Developer Certificate of Origin sign-off on every commit.

## 2. Classify workflows by trust level

Decide whether each workflow can run code from fork pull requests.

- Use GitHub-hosted runners for untrusted pull request code by default.
- Do not expose repository secrets to fork pull requests.
- Do not run untrusted pull request code on a self-hosted runner. Keep trusted
  jobs on a separate event and document who can trigger them.
- Grant the workflow only the
  [minimum `GITHUB_TOKEN` permissions](https://docs.github.com/actions/security-for-github-actions/security-guides/automatic-token-authentication#modifying-the-permissions-for-the-github_token)
  it needs.

Record the decision next to the workflow so later changes do not silently widen
its permissions.

## 3. Select a runner

Start with `ubuntu-latest` unless the job has a measured need for another
architecture, GPU, memory, or CPU capacity.

For workloads that need CNCF infrastructure, choose a label from the
[CNCF hosted runner registry](../runners/cncf-runners.md). Confirm access and
fork safety with the Kubeflow maintainers before using a self-hosted label in a
pull request workflow.

## 4. Add the baseline source checks

At minimum, run formatting, linting, unit tests, and the shared Apache 2.0
header check. Pin shared actions to a full commit SHA and update the pin
deliberately.

```yaml
name: Verify source

on:
  pull_request:
  push:
    branches:
      - main

permissions:
  contents: read

jobs:
  verify-boilerplate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
        with:
          fetch-depth: 0
      - uses: kubeflow/testing/.github/actions/verify-boilerplate@8483606e0f8a34bf647f3b62a516efa17096c58c
        with:
          base-ref: main
```

If the repository uses a different default branch, replace `main`. The action
also supports `boilerplate-dir`, `root-dir`, and `exclude`; see the
[shared action definition](../.github/actions/verify-boilerplate/action.yml).

Keep language-specific checks in separate jobs so failures identify the broken
contract directly.

## 5. Choose an end-to-end cluster strategy

Use the smallest environment that proves the behavior.

1. Prefer a local KinD cluster on a GitHub-hosted runner for pull request tests.
2. Cache images and dependencies only when the cache cannot be written by
   untrusted code and restored by a more privileged job.
3. Use a self-hosted or cloud cluster only when KinD cannot cover the test.
   Put provisioning, test execution, and cleanup in the same trusted workflow.
4. Set explicit timeouts and make cleanup run after failure or cancellation.
5. Never give a pull request from a fork direct access to cluster credentials.

Document the Kubernetes version, required add-ons, expected runtime, and the
reason the selected environment is necessary.

## 6. Make checks reproducible locally

For every required CI job, provide a local command in the repository README or
`Makefile`. Pin tool versions used by both paths. A contributor should be able
to reproduce formatting, lint, unit-test, and manifest-generation failures
without access to hosted infrastructure.

## 7. Protect the default branch

After the workflows pass on a pull request:

- require the deterministic source and test jobs before merge;
- require review from the relevant `OWNERS` approvers;
- keep privileged deployment or release jobs outside the untrusted pull
  request path;
- document who can rerun trusted jobs and how flaky infrastructure failures are
  handled.

## 8. Verify the first pull request

Before declaring onboarding complete, open a small pull request from a fork and
confirm:

- untrusted jobs run without secrets;
- required checks report a useful failure and success state;
- DCO, review, and approval automation respond as expected;
- the chosen runner label is available;
- the local commands match CI; and
- any cluster resources are cleaned up when a job fails.

Revisit this checklist when the repository adds a new runner class, secret,
deployment target, or required check.
