# Experiment interruption audit

Checked on 20 September 2026 against retained Windows System events and completed model artifacts. Times below are Asia/Dhaka local time.

## Available system evidence

| Event recorded | Event ID | Evidence |
| --- | --- | --- |
| 14 September 08:01:38 | 41 | Restart following an unclean shutdown |
| 14 September 13:51:38 | 41 | Restart following an unclean shutdown |
| 14 September 22:29:10 | 41 | Restart following an unclean shutdown |
| 14 September 23:17:20 | 41 | Restart following an unclean shutdown |

Companion event 6008 records also report unexpected shutdowns. These events establish machine-level interruptions during the experiment period. They do not identify whether power loss, a system crash or another condition caused them. Some recorded shutdown times do not align exactly with the observed case timestamps; they must not be used to assign a precise cause to every process stop. The exact cause of every individual interruption cannot be recovered from the evidence inspected.

## Status and recovery

The prior running/waiting JSON files survived terminated processes. Such files describe the last recorded state, not a live health check. Process checks were required before resuming. Windows virtual-environment launchers may show two Python processes for one logical evaluation; this alone is not evidence of duplicate runs.

The final manifests now report complete for all three models. Each has 400 distinct source/target/row cases, 100 cases per source/target combination and 20 paired explanations per combination. The finalizer independently checked these counts and completed successfully on 15 September at 02:23:26 UTC, publishing commit 1497e1e. Recovery preserved completed cases; the later concurrency change was documented separately from the frozen numerical protocol.

No evidence establishes that all interruptions were caused by automatic sleep. Sleep and display timeouts were set to Never at the user's request; this does not prevent power loss or operating-system restarts.

The investigation is resolved at this evidence level. Durable future execution should use explicit process-aware status and system-event correlation; this audit does not claim that the supervisor can survive a reboot.
