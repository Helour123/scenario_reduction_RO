# Objective 2 results / 实验结果

162 records; regenerated from runs.csv. Existing experiments were not rerun for the plotting refactor.

Time-limited solves: 22. Maximum relative MIP gap: 49.1%.

Joint exclusion is parameter-sensitive and is not consistently better than sequential cleaning. Oracle and protected methods use true labels. This is a synthetic pilot, not evidence of general superiority.

| Framework | Contamination | Method | Lambda | Mean regret | SD | Tail retained | Mean MIP gap |
|---|---|---|---|---|---|---|---|
| SP | 0.0 | full_observed |  | 0.569 | 0.888 | 100.0% | 0 |
| SP | 0.0 | oracle_clean_full |  | 0.569 | 0.888 | 100.0% | 0 |
| SP | 0.0 | selection_only | 2.0 | 4.697 | 1.955 | 100.0% | 0 |
| SP | 0.0 | clean_then_select | 2.0 | 4.697 | 1.955 | 100.0% | 0 |
| SP | 0.0 | joint_anomaly | 2.0 | 4.697 | 1.955 | 100.0% | 0 |
| SP | 0.0 | joint_quality | 0.5 | 4.697 | 1.955 | 100.0% | 0 |
| SP | 0.0 | joint_quality | 2.0 | 4.697 | 1.955 | 100.0% | 0 |
| SP | 0.0 | joint_quality | 8.0 | 4.697 | 1.955 | 100.0% | 0 |
| SP | 0.0 | joint_quality_protected | 2.0 | 4.697 | 1.955 | 100.0% | 0 |
| RO | 0.0 | full_observed |  | 27.833 | 9.011 | 100.0% | 0 |
| RO | 0.0 | oracle_clean_full |  | 27.833 | 9.011 | 100.0% | 0 |
| RO | 0.0 | selection_only | 2.0 | 28.358 | 14.230 | 100.0% | 0.0022 |
| RO | 0.0 | clean_then_select | 2.0 | 28.358 | 14.230 | 100.0% | 0.0022 |
| RO | 0.0 | joint_anomaly | 2.0 | 26.181 | 11.524 | 100.0% | 0.231 |
| RO | 0.0 | joint_quality | 0.5 | 51.073 | 30.508 | 41.7% | 0.414 |
| RO | 0.0 | joint_quality | 2.0 | 28.217 | 12.524 | 100.0% | 0.21 |
| RO | 0.0 | joint_quality | 8.0 | 27.146 | 13.134 | 100.0% | 9.58e-16 |
| RO | 0.0 | joint_quality_protected | 2.0 | 25.172 | 10.771 | 100.0% | 0.0972 |
| SP | 0.1 | full_observed |  | 10.052 | 6.668 | 100.0% | 0 |
| SP | 0.1 | oracle_clean_full |  | 0.548 | 0.902 | 100.0% | 0 |
| SP | 0.1 | selection_only | 2.0 | 3.393 | 2.097 | 100.0% | 0 |
| SP | 0.1 | clean_then_select | 2.0 | 2.863 | 2.746 | 100.0% | 0 |
| SP | 0.1 | joint_anomaly | 2.0 | 3.393 | 2.097 | 100.0% | 0 |
| SP | 0.1 | joint_quality | 0.5 | 2.863 | 2.746 | 100.0% | 0 |
| SP | 0.1 | joint_quality | 2.0 | 2.863 | 2.746 | 100.0% | 0 |
| SP | 0.1 | joint_quality | 8.0 | 3.393 | 2.097 | 100.0% | 0 |
| SP | 0.1 | joint_quality_protected | 2.0 | 2.863 | 2.746 | 100.0% | 0 |
| RO | 0.1 | full_observed |  | 116.570 | 34.077 | 100.0% | 0 |
| RO | 0.1 | oracle_clean_full |  | 27.833 | 9.011 | 100.0% | 0 |
| RO | 0.1 | selection_only | 2.0 | 125.249 | 31.735 | 100.0% | 0.00279 |
| RO | 0.1 | clean_then_select | 2.0 | 35.519 | 24.005 | 100.0% | 0.00239 |
| RO | 0.1 | joint_anomaly | 2.0 | 39.179 | 19.998 | 100.0% | 0.185 |
| RO | 0.1 | joint_quality | 0.5 | 28.977 | 11.460 | 80.6% | 0.421 |
| RO | 0.1 | joint_quality | 2.0 | 21.477 | 13.265 | 100.0% | 0.153 |
| RO | 0.1 | joint_quality | 8.0 | 53.850 | 38.827 | 100.0% | 0.00589 |
| RO | 0.1 | joint_quality_protected | 2.0 | 21.477 | 13.265 | 100.0% | 0.121 |
| SP | 0.2 | full_observed |  | 84.840 | 5.307 | 100.0% | 0 |
| SP | 0.2 | oracle_clean_full |  | 1.984 | 3.289 | 100.0% | 0 |
| SP | 0.2 | selection_only | 2.0 | 84.840 | 5.307 | 100.0% | 0 |
| SP | 0.2 | clean_then_select | 2.0 | 3.277 | 2.208 | 100.0% | 0 |
| SP | 0.2 | joint_anomaly | 2.0 | 81.588 | 9.778 | 100.0% | 0 |
| SP | 0.2 | joint_quality | 0.5 | 3.277 | 2.208 | 100.0% | 0 |
| SP | 0.2 | joint_quality | 2.0 | 25.157 | 40.070 | 100.0% | 0 |
| SP | 0.2 | joint_quality | 8.0 | 81.588 | 9.778 | 100.0% | 0 |
| SP | 0.2 | joint_quality_protected | 2.0 | 28.410 | 45.703 | 100.0% | 0 |
| RO | 0.2 | full_observed |  | 121.694 | 21.627 | 100.0% | 0 |
| RO | 0.2 | oracle_clean_full |  | 27.833 | 9.011 | 100.0% | 0 |
| RO | 0.2 | selection_only | 2.0 | 120.400 | 17.655 | 100.0% | 0.00297 |
| RO | 0.2 | clean_then_select | 2.0 | 34.966 | 2.814 | 100.0% | 0.003 |
| RO | 0.2 | joint_anomaly | 2.0 | 88.644 | 12.707 | 100.0% | 0.12 |
| RO | 0.2 | joint_quality | 0.5 | 50.616 | 30.337 | 88.9% | 0.437 |
| RO | 0.2 | joint_quality | 2.0 | 58.600 | 20.060 | 100.0% | 0.0359 |
| RO | 0.2 | joint_quality | 8.0 | 70.226 | 27.994 | 100.0% | 0.00303 |
| RO | 0.2 | joint_quality_protected | 2.0 | 58.600 | 20.060 | 100.0% | 0.0806 |

Plots: see plots/. Read README.md for definitions, evaluation domains and limitations.
RO bounds cover non-excluded scenarios at checked decisions only. Complete newsvendor recourse does not test uncertain-constraint feasibility.