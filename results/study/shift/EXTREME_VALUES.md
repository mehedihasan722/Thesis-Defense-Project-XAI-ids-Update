# Extreme raw rate-value audit

In the cleaned IDS2018 release, 213 finite rate values on 211 rows exceed float32 range out of 17129715 rows. Counts are streamed from both SECOND_BYTES fields. The audit does not determine the exporter or cleaning cause.

The study applies the predeclared signed-log encoding to all models and hashes that float32-equivalent representation before splitting. This prevents numerical overflow but does not establish physical validity of the original values. No post-test replacement or clipping is introduced. A separate predeclared data-cleaning sensitivity study would be needed to quantify their impact.

| Seed | Split | Sampled rows | Rows with extreme raw rates |
| --- | --- | --- | --- |
| 42 | train | 200000 | 5 |
| 42 | validation | 40000 | 1 |
| 42 | test | 80000 | 0 |
| 7 | train | 200000 | 3 |
| 7 | validation | 40000 | 0 |
| 7 | test | 80000 | 3 |
| 1337 | train | 200000 | 3 |
| 1337 | validation | 40000 | 1 |
| 1337 | test | 80000 | 3 |
