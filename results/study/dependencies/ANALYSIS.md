# Dependency graph and execution capacity audit

Snapshot: 14 September 2026, approximately 08:21 Asia/Dhaka.

GitHub's dependency graph is populated. The exported SPDX inventory contains 69 package records, which may include the root project; this is not necessarily 69 distinct third-party dependencies. See [export](github-sbom.spdx.json) and [audit metadata](audit.json).

The installed study runtime passes `pip check`. This checks declared dependency consistency, not vulnerability absence. The Dependabot alerts endpoint returned HTTP 403 with the available credential. Alert status is therefore unknown; an empty captured list must not be interpreted as zero vulnerabilities.

Monthly Dependabot proposals now cover Python manifests in /study as well as GitHub Actions. Proposals require review; nothing is automatically merged. The running environment and scientific dependency pins were not upgraded. Any accepted scientific dependency change requires compatibility tests and consideration of checkpoint signatures before reuse.

The graph displays packages listed in the frozen lock as direct dependencies. A flat environment freeze does not by itself describe the application's true direct/transitive dependency hierarchy.

## Concurrent model decision

The machine reported 16,640,016 KiB total visible memory and 2,546,316 KiB free (approximately 15.9 GiB total and 2.4 GiB free). SmolLM2 has about 1.7 billion parameters: float32 weights alone require approximately 6.3 GiB, before inference buffers and other overhead. Starting it concurrently cannot be justified with this headroom. The existing sequential runner remains responsible for starting it after TinyLlama exits.

Progress observed during this audit: Qwen 400/400 complete; TinyLlama 195/400 saved and running; SmolLM2 queued. These are dated observations, not a live monitor. Check current manifests and processes for later status. Checkpoints continue to preserve completed cases.
