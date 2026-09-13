# GitHub project workflow

| GitHub area | Repository support |
| --- | --- |
| Code | README links to measured results, protocol, figures and progress; model revisions and environment are pinned |
| Issues | Forms for bugs, experiment proposals and result audits |
| Pull requests | Template covering rationale, experimental impact and validation |
| Actions | Protocol CI runs dataset-free tests, dependency checks and figure-link checks on pushes/PRs or manual dispatch |
| Security and quality | Security reporting guidance, read-only CI permissions and pinned action revisions; monthly Dependabot action-update proposals |
| Projects / Wiki | Current progress and research ledger remain versioned in Markdown; no duplicate board or wiki is required for these workflows |
| Insights | GitHub derives activity and community information from repository history and these contribution files |

The CI workflow does not train models, download datasets or request API credentials. Full LLM and research runs remain local and checkpointed. CI success is a code/protocol check, not proof that every scientific conclusion is correct.

Action updates are proposed for review, not automatically merged. Scientific dependency versions remain pinned; deliberate environment changes require protocol review.

References: [GitHub workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax), [issue forms](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms).
