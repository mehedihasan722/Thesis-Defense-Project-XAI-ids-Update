# GitHub project workflow

| GitHub area | Repository support |
| --- | --- |
| Code | README links to measured results, protocol, figures and progress; model revisions and environment are pinned |
| Issues | Forms for bugs, experiment proposals and result audits |
| Pull requests | Template covering rationale, experimental impact and validation |
| Actions | Protocol CI runs dataset-free tests, dependency checks and figure-link checks on pushes/PRs or manual dispatch |
| Security and quality | Security reporting guidance, read-only CI permissions and pinned action revisions; monthly Dependabot action-update proposals |
| Wiki | [Published guide](https://github.com/mehedihasan722/Thesis-Defense-Project-XAI-ids-Update/wiki) covers setup, protocol, evidence navigation and metric interpretation; numerical evidence remains versioned in this repository |
| Projects | No board configured yet; current progress remains in PROGRESS.md. A board can track To do, Running, Review and Done without duplicating result tables |
| Insights | GitHub derives activity and community information from repository history and these contribution files |

The CI workflow does not train models, download datasets or request API credentials. Full LLM and research runs remain local and checkpointed. CI success is a code/protocol check, not proof that every scientific conclusion is correct.

Action updates are proposed for review, not automatically merged. Scientific dependency versions remain pinned; deliberate environment changes require protocol review.

References: [GitHub workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax), [issue forms](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms).

## Task completion updates

Track concrete problems and remaining work in GitHub Issues. After a task is verified, update its checklist and add the evidence or commit link; close only when every acceptance criterion is satisfied. Record partial progress without declaring completion.

- [Fix completed LLM summary failure with list-valued metrics](https://github.com/mehedihasan722/Thesis-Defense-Project-XAI-ids-Update/issues/3) — closed at creation.
- [Complete TinyLlama and SmolLM2 classification and explanation runs](https://github.com/mehedihasan722/Thesis-Defense-Project-XAI-ids-Update/issues/4) — open at creation.
- [Finish LLM masking validation, matched analysis and final figures](https://github.com/mehedihasan722/Thesis-Defense-Project-XAI-ids-Update/issues/5) — open at creation.
- [Investigate interrupted experiment processes and stale running status](https://github.com/mehedihasan722/Thesis-Defense-Project-XAI-ids-Update/issues/6) — open at creation.

## GitHub Agents

Repository-wide guidance is in [.github/copilot-instructions.md](../.github/copilot-instructions.md). It describes the research protocol, dataset-free tests, checkpoint constraints and issue-completion requirements.

The Agents page displays GitHub-hosted agent sessions. Adding instructions configures repository context; it does not start a session or move the existing local experiments to GitHub. No hosted session was launched as part of this setup. Use a bounded code or documentation issue for any future hosted task; local data-dependent experiment execution remains with the existing runner.

Reference: [GitHub repository custom instructions](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions).
