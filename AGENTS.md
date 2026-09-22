# Project tool usage

Optional user-installed tools are documented in `docs/DEVELOPMENT_TOOLS.md`.

- Ponytail is available as a user skill. Prefer existing code and standard libraries while preserving research validation, audit evidence and required checks.
- Graphifyy is available as the `graphify` skill and CLI. Follow `.graphifyignore` when indexing this repository. Treat extracted or inferred graph relationships as navigation aids, not experimental evidence.
- RTK is available as `rtk` (Windows fallback: `$env:USERPROFILE/.local/bin/rtk.exe`). Use it for supported routine inspection commands such as `rtk git status`. Read `RTK.md` for output handling.

Keep tool installations separate from `.venv-study`. Do not change completed experiment protocols or reported results to satisfy tool advice. User instructions and scientific reproducibility requirements take priority over optional simplification guidance.
