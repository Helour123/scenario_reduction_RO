# Continuous entropy / MILP comparison

Raw and repaired results have different meanings. Repaired results use exactly K hard representatives and hard deletion, with LP transport refit.
Raw partial deletion changes the model. Raw RO includes every positive-weight support; fractional selection does not imply K scenarios.
Seconds include entropy multistart and hard repair; SLSQP time limits are cooperative. MILP gaps are in runs.csv. No global bound exists for local entropy runs.
Zero entropy tolerances preserve the discrete feasible set. Failed local solves do not prove infeasibility; feasible hard LP starts may be returned.

| Framework | Contamination | Method | Stage | Mean regret | SD | Seconds | Fractional z/o | Fallbacks |
|---|---|---|---|---|---|---|---|---|
| SP | 0% | milp | hard | 40.076 | 42.998 | 0.00 | 0.0/0.0 | 0 |
| SP | 0% | partial | raw | 40.076 | 42.998 | 0.08 | 0.0/0.0 | 0 |
| SP | 0% | partial | repaired | 40.076 | 42.998 | 0.08 | 0.0/0.0 | 0 |
| SP | 0% | double | raw | 40.076 | 42.998 | 0.06 | 0.0/0.0 | 0 |
| SP | 0% | double | repaired | 40.076 | 42.998 | 0.06 | 0.0/0.0 | 0 |
| SP | 0% | continuation | raw | 40.076 | 42.998 | 0.17 | 0.0/0.0 | 0 |
| SP | 0% | continuation | repaired | 40.076 | 42.998 | 0.17 | 0.0/0.0 | 0 |
| RO | 0% | milp | hard | 19.892 | 7.541 | 0.09 | 0.0/0.0 | 0 |
| RO | 0% | partial | raw | 26.688 | 2.069 | 0.40 | 3.5/1.5 | 0 |
| RO | 0% | partial | repaired | 57.355 | 45.439 | 0.40 | 0.0/0.0 | 0 |
| RO | 0% | double | raw | 19.892 | 7.541 | 0.42 | 4.0/1.0 | 0 |
| RO | 0% | double | repaired | 41.248 | 22.661 | 0.42 | 0.0/0.0 | 0 |
| RO | 0% | continuation | raw | 19.892 | 7.541 | 1.44 | 4.0/1.0 | 0 |
| RO | 0% | continuation | repaired | 41.248 | 22.661 | 1.44 | 0.0/0.0 | 0 |
| SP | 10% | milp | hard | 40.095 | 42.972 | 0.00 | 0.0/0.0 | 0 |
| SP | 10% | partial | raw | 40.095 | 42.972 | 0.09 | 0.0/0.0 | 0 |
| SP | 10% | partial | repaired | 40.095 | 42.972 | 0.09 | 0.0/0.0 | 0 |
| SP | 10% | double | raw | 40.095 | 42.972 | 0.11 | 0.0/0.0 | 0 |
| SP | 10% | double | repaired | 40.095 | 42.972 | 0.11 | 0.0/0.0 | 0 |
| SP | 10% | continuation | raw | 40.095 | 42.972 | 0.29 | 0.0/0.0 | 0 |
| SP | 10% | continuation | repaired | 40.095 | 42.972 | 0.29 | 0.0/0.0 | 0 |
| RO | 10% | milp | hard | 46.829 | 30.554 | 0.05 | 0.0/0.0 | 0 |
| RO | 10% | partial | raw | 41.654 | 22.087 | 0.24 | 4.0/2.0 | 0 |
| RO | 10% | partial | repaired | 41.654 | 22.087 | 0.24 | 0.0/0.0 | 0 |
| RO | 10% | double | raw | 41.654 | 22.087 | 0.32 | 4.0/1.0 | 0 |
| RO | 10% | double | repaired | 41.654 | 22.087 | 0.32 | 0.0/0.0 | 0 |
| RO | 10% | continuation | raw | 41.654 | 22.087 | 1.16 | 4.0/1.0 | 0 |
| RO | 10% | continuation | repaired | 41.654 | 22.087 | 1.16 | 0.0/0.0 | 0 |
| SP | 20% | milp | hard | 85.111 | 20.000 | 0.00 | 0.0/0.0 | 0 |
| SP | 20% | partial | raw | 85.111 | 20.000 | 0.09 | 0.0/0.0 | 0 |
| SP | 20% | partial | repaired | 85.111 | 20.000 | 0.09 | 0.0/0.0 | 0 |
| SP | 20% | double | raw | 85.111 | 20.000 | 0.10 | 0.0/0.0 | 0 |
| SP | 20% | double | repaired | 85.111 | 20.000 | 0.10 | 0.0/0.0 | 0 |
| SP | 20% | continuation | raw | 85.111 | 20.000 | 0.30 | 0.0/0.0 | 0 |
| SP | 20% | continuation | repaired | 85.111 | 20.000 | 0.30 | 0.0/0.0 | 0 |
| RO | 20% | milp | hard | 29.161 | 13.653 | 0.03 | 0.0/0.0 | 0 |
| RO | 20% | partial | raw | 33.977 | 12.232 | 0.26 | 4.5/2.0 | 0 |
| RO | 20% | partial | repaired | 22.417 | 4.116 | 0.26 | 0.0/0.0 | 0 |
| RO | 20% | double | raw | 33.977 | 12.232 | 0.25 | 4.0/1.0 | 0 |
| RO | 20% | double | repaired | 22.417 | 4.116 | 0.25 | 0.0/0.0 | 0 |
| RO | 20% | continuation | raw | 33.977 | 12.232 | 0.81 | 4.0/1.0 | 0 |
| RO | 20% | continuation | repaired | 22.417 | 4.116 | 0.81 | 0.0/0.0 | 0 |