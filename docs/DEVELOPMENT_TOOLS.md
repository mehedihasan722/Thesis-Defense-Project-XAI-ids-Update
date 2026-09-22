# Installed development tools

Installed and smoke-tested on 22 September 2026. These are development aids, not additional evaluated intrusion-detection models. The thesis Python environment and completed numerical results were not changed by installation.

| Tool | Installed source | Integration |
| --- | --- | --- |
| Ponytail | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail), commit `e3ba2aa6f1e6f0bc4d69eb09c9f0d0a93af56156` | `skills/ponytail` installed to the user's `.codex/skills/ponytail` using the Codex skill installer. |
| Graphifyy 0.4.25 | [EaZtoday/graphifyy](https://github.com/EaZtoday/graphifyy), commit `215b5d40e78e498100cbf8855224331c40f757d9` | Isolated `uv tool` environment; `graphify install --platform codex` registered the skill in the user's `.agents/skills/graphify`. |
| RTK 0.49.0 | [rtk-ai/rtk release](https://github.com/rtk-ai/rtk/releases/tag/v0.49.0) | Windows x86-64 binary installed in the user's `.local/bin`; project instructions in `RTK.md`. |

The user confirmed the EaZtoday Graphifyy repository. Its README identifies `safishamsi/graphify` as the upstream official repository; this installation deliberately uses the confirmed fork at an immutable commit rather than silently substituting a PyPI package or upstream revision.

## Checks performed

- Ponytail installer completed and the installed skill's name/front matter was checked.
- Graphifyy CLI help and Codex skill registration succeeded.
- Graphifyy's deterministic tree-sitter extraction parsed `study/models.py`: **11 nodes and 20 edges**. This was a local installation smoke check, not a full project knowledge graph.
- RTK reported `rtk 0.49.0` and successfully ran `rtk git status --short`.
- RTK archive checksum matched the release asset digest: `cb971046598f0e8bd51f6c27780fcdd2c39a4c459a811bd95b0d77ba8c0d7c9f`.

## Use

The skills are available on the next turn. Request Ponytail by name for coding simplification or Graphify for knowledge-graph work. CLI examples:

```powershell
graphify --help
rtk --version
rtk git status --short
rtk gain
```

If this app session has an older PATH, invoke `$env:USERPROFILE/.local/bin/graphify.exe` or `$env:USERPROFILE/.local/bin/rtk.exe` explicitly. Both executables are in that existing user tools directory.

Graph indexing should exclude raw releases, model weights, environments, logs and temporary outputs using `.graphifyignore`. Full graph generation is a separate operation; semantic edges must be labeled and checked against their sources. No automatic indexing, paid API calls, global multi-agent configuration changes or command hooks were added by this setup.

RTK is used through project instructions rather than a hook. For exact scientific output use native commands or `rtk proxy`. Neither command-output compression nor Ponytail simplification validates thesis findings.

## Reproduce or remove

Graphifyy can be installed independently of the study environment:

```powershell
uv tool install 'git+https://github.com/EaZtoday/graphifyy.git@215b5d40e78e498100cbf8855224331c40f757d9'
graphify install --platform codex
```

Ponytail's pinned source is `skills/ponytail` at the commit above. Use the Codex skill installer for that path. RTK's pinned Windows release archive is available from the linked release; verify its SHA-256 before extracting `rtk.exe`.

To remove Graphifyy's executable/environment use `uv tool uninstall graphifyy`; its installed skill directory is separate. Ponytail is a user skill directory, and RTK is a standalone user executable. Remove only the corresponding tool's files if uninstalling. No experiment environment restoration is needed.
