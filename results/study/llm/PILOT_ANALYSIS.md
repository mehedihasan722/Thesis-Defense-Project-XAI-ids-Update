# LLM pilot: first-case qualitative check

Pilot evidence, not a benchmark estimate. Qwen/Qwen2.5-0.5B-Instruct on UNSW row 1476691 predicted Benign (0), while the dataset label was Attack (1). The self-explanation listed many features and was truncated, so it fails the required JSON/maximum-three-feature check.

The detector prompt supplied positive probability drops for max_ttl (0.980812), server_tcp_flags (0.294095), and min_ttl (0.124040). The generated detector explanation instead named duration_in and duration_out and discussed a negative drop. Those features and that sign were not supported by the supplied evidence. This is a concrete grounding failure; it must not be counted as a successful explanation merely because it sounds plausible or parses as JSON.

The exact prompt and unmodified output are preserved in the pilot cases.jsonl. The full-run summary checks allowed feature names and evidence membership separately. Those automatic checks still do not verify every prose claim. Do not generalize from this one inspected case to all models or the entire dataset, and do not tune the experiment to erase the failure.
