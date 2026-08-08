# Skill Benchmark: weekly-report-generator

**Model**: deepseek-v4-pro[1m]
**Date**: 2026-08-08T20:18:13Z
**Evals**: 1, 2, 3 (1 run each per configuration)

## Summary

| Metric | With Skill | Without Skill | Delta |
|--------|------------|---------------|-------|
| Pass Rate | 92% ± 14% | 83% ± 19% | +0.08 |
| Time | 600.8s ± 151.1s | 460.7s ± 74.3s | +140.1s |
| Tokens | 23015 ± 7319 | 16848 ± 2879 | +6167 |

## Per-Eval Details

| Eval | Config | Pass Rate | Time | Tokens |
|------|--------|-----------|------|--------|
| 1 | with_skill | 100% (8/8) | 430.9s | 17455 |
| 1 | without_skill | 88% (7/8) | 544.0s | 20099 |
| 2 | with_skill | 75% (6/8) | 720.1s | 31307 |
| 2 | without_skill | 62% (5/8) | 436.9s | 14619 |
| 3 | with_skill | 100% (8/8) | 651.5s | 20284 |
| 3 | without_skill | 100% (8/8) | 401.3s | 15827 |
