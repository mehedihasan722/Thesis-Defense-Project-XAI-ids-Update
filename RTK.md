# RTK usage in this research project

RTK 0.49.0 is installed in the user's `.local/bin` directory. Its Windows archive SHA-256 was verified against the GitHub release asset digest before execution.

Examples:

```powershell
rtk --version
rtk git status --short
rtk gain
rtk proxy git diff --check
```

RTK filters supported command output. Condensed output is a convenience, not a replacement for full scientific evidence. Use native commands or `rtk proxy` when inspecting raw metrics, errors, complete logs, signatures or exact reproducibility outputs. Preserve original exit codes and required validation.

Codex integration here is instruction-based. No automatic command interception hook is installed. Unsupported shell syntax and PowerShell built-ins should be run natively rather than blindly prefixed with RTK.
