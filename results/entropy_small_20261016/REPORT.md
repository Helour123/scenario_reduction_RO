# Continuous entropy / MILP comparison

Raw and repaired results have different meanings. Repaired results use exactly K hard representatives and hard deletion, with LP transport refit.
Raw partial deletion changes the model. Raw RO includes every positive-weight support; fractional selection does not imply K scenarios.
Seconds include entropy multistart and hard repair; SLSQP time limits are cooperative. MILP gaps are in runs.csv. No global bound exists for local entropy runs.
Zero entropy tolerances preserve the discrete feasible set. Failed local solves do not prove infeasibility; feasible hard LP starts may be returned.

| Framework | Contamination | Method | Stage | Mean regret | SD | Seconds | Fractional z/o | Fallbacks |
|---|---|---|---|---|---|---|---|---|
| SP | 0% | milp | hard | 38.913 | 35.534 | 0.02 | 0.0/0.0 | 0 |
| SP | 0% | partial | raw | 38.913 | 35.534 | 0.41 | 0.0/0.0 | 0 |
| SP | 0% | partial | repaired | 38.913 | 35.534 | 0.41 | 0.0/0.0 | 0 |
| SP | 0% | double | raw | 38.913 | 35.534 | 0.45 | 0.0/0.0 | 0 |
| SP | 0% | double | repaired | 38.913 | 35.534 | 0.45 | 0.0/0.0 | 0 |
| SP | 0% | continuation | raw | 38.913 | 35.534 | 1.58 | 0.0/0.0 | 0 |
| SP | 0% | continuation | repaired | 38.913 | 35.534 | 1.58 | 0.0/0.0 | 0 |
| RO | 0% | milp | hard | 34.171 | 8.365 | 0.13 | 0.0/0.0 | 0 |
| RO | 0% | partial | raw | 30.937 | 4.226 | 2.31 | 4.7/2.0 | 0 |
| RO | 0% | partial | repaired | 45.421 | 24.150 | 2.31 | 0.0/0.0 | 0 |
| RO | 0% | double | raw | 30.937 | 4.226 | 2.51 | 4.3/1.3 | 0 |
| RO | 0% | double | repaired | 45.421 | 24.150 | 2.51 | 0.0/0.0 | 0 |
| RO | 0% | continuation | raw | 33.696 | 4.560 | 3.25 | 2.7/0.7 | 1 |
| RO | 0% | continuation | repaired | 63.836 | 22.209 | 3.25 | 0.0/0.0 | 1 |
| SP | 10% | milp | hard | 50.326 | 43.790 | 0.01 | 0.0/0.0 | 0 |
| SP | 10% | partial | raw | 50.326 | 43.790 | 0.50 | 0.0/0.0 | 0 |
| SP | 10% | partial | repaired | 50.326 | 43.790 | 0.50 | 0.0/0.0 | 0 |
| SP | 10% | double | raw | 50.326 | 43.790 | 0.45 | 0.0/0.0 | 0 |
| SP | 10% | double | repaired | 50.326 | 43.790 | 0.45 | 0.0/0.0 | 0 |
| SP | 10% | continuation | raw | 50.326 | 43.790 | 1.73 | 0.0/0.0 | 0 |
| SP | 10% | continuation | repaired | 50.326 | 43.790 | 1.73 | 0.0/0.0 | 0 |
| RO | 10% | milp | hard | 37.115 | 16.833 | 0.22 | 0.0/0.0 | 0 |
| RO | 10% | partial | raw | 61.918 | 29.714 | 1.47 | 4.3/4.3 | 0 |
| RO | 10% | partial | repaired | 80.144 | 52.356 | 1.47 | 0.0/0.0 | 0 |
| RO | 10% | double | raw | 40.937 | 12.370 | 1.89 | 2.3/0.7 | 0 |
| RO | 10% | double | repaired | 70.704 | 54.776 | 1.89 | 0.0/0.0 | 0 |
| RO | 10% | continuation | raw | 40.937 | 12.370 | 3.23 | 1.7/0.7 | 1 |
| RO | 10% | continuation | repaired | 70.704 | 54.776 | 3.23 | 0.0/0.0 | 1 |
| SP | 20% | milp | hard | 96.480 | 29.053 | 0.01 | 0.0/0.0 | 0 |
| SP | 20% | partial | raw | 96.480 | 29.053 | 0.43 | 0.0/0.0 | 0 |
| SP | 20% | partial | repaired | 96.480 | 29.053 | 0.43 | 0.0/0.0 | 0 |
| SP | 20% | double | raw | 96.480 | 29.053 | 0.49 | 0.0/0.0 | 0 |
| SP | 20% | double | repaired | 96.480 | 29.053 | 0.49 | 0.0/0.0 | 0 |
| SP | 20% | continuation | raw | 96.480 | 29.053 | 1.84 | 0.0/0.0 | 0 |
| SP | 20% | continuation | repaired | 96.480 | 29.053 | 1.84 | 0.0/0.0 | 0 |
| RO | 20% | milp | hard | 44.898 | 22.454 | 0.27 | 0.0/0.0 | 0 |
| RO | 20% | partial | raw | 44.449 | 22.491 | 1.55 | 4.3/2.0 | 0 |
| RO | 20% | partial | repaired | 44.449 | 22.491 | 1.55 | 0.0/0.0 | 0 |
| RO | 20% | double | raw | 63.505 | 25.192 | 1.73 | 4.0/1.0 | 0 |
| RO | 20% | double | repaired | 48.979 | 18.413 | 1.73 | 0.0/0.0 | 0 |
| RO | 20% | continuation | raw | 61.350 | 28.782 | 3.09 | 4.0/1.0 | 0 |
| RO | 20% | continuation | repaired | 46.823 | 20.948 | 3.09 | 0.0/0.0 | 0 |