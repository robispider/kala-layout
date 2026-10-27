# Empirical typing pipeline

Status: **insufficient_data**; training performed: **False**.

4 sessions; 2 contributor IDs. 547 position labels recovered as a derived field; raw labels and packages preserved.

Eligible intervals: 1076 primary; 1320 including idle-flagged sessions. Recorded score denominators are unchanged.

Tables include every candidate, its provenance and reasons for exclusion. Negative flight is retained as key overlap. Modifier/Shift events and autorepeats have separate identities. The frozen effort column is a physical-key feature, not milliseconds or a new layout score.

| Protocol | Bank | Build | Eligible contributors | Eligible intervals | Gates |
| --- | --- | --- | --- | --- | --- |
| 2026.10-literature-r3 | 1.3.0 | Debug | 0 | 0 | contributor_interval_floor, engine_replay_validation_pending, near_duplicate_family_review_pending, observed_pilot_pending, too_few_independent_contributors, too_few_prompt_families |
| 2026.10-literature-r4 | 1.4.0 | Release | 1 | 329 | contributor_session_replication_floor, engine_replay_validation_pending, mapping_registry_incomplete, near_duplicate_family_review_pending, observed_pilot_pending, too_few_independent_contributors |
| 2026.10-literature-r5 | 1.4.0 | Debug | 1 | 343 | contributor_session_replication_floor, engine_replay_validation_pending, mapping_registry_incomplete, near_duplicate_family_review_pending, observed_pilot_pending, too_few_independent_contributors, too_few_prompt_families |
| 2026.10-r1 | 1.0.0 | Debug | 1 | 404 | contributor_session_replication_floor, engine_replay_validation_pending, near_duplicate_family_review_pending, observed_pilot_pending, too_few_independent_contributors |

No model was inferred from the number of keystrokes. Engineering floors are not a sample-size power analysis. Observed physical-key, consent, offline retry, receiver restart and withdrawal scenarios remain required.
