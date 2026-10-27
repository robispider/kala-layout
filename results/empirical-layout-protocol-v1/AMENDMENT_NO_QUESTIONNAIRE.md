# Amendment: no questionnaire and no assumed person identity

Date: 27 October 2026, Asia/Dhaka. Protocol revision: BHE-v1.1-draft-2026-10-27. Status: documentation only; no collection or fitting code changed.

## Decision

Yes, the protocol needs this revision. The technical mitigation plan is mostly sound, but its questionnaire, person-linkage and independent-person-count requirements do not fit the intended collection. They are replaced in the current [protocol](RESEARCH_PROTOCOL.md), especially sections 2, 4, 6 and 10–12.

A questionnaire is not required to learn action costs. Some answers may be useful in other studies, but their reliability and participant burden are reasons not to make this project depend on them. Removing the questions leaves familiarity and technique partly unmeasured; automatic timing metrics cannot fully reconstruct them.

## What stays and what changes

| Earlier mitigation | Revised decision |
| --- | --- |
| Collect every physical action and exact text/engine change | Keep; essential for Shift, Space, zero-output prefixes and composition |
| Verify capture boundaries, held keys, replay, retries and withdrawal | Keep; an observed pilot is still necessary |
| Add experience, finger-count, usual-hand and device questionnaires | Remove; use observable fields and explicit unknowns |
| Recover a stable person identity across computers | Remove as a requirement; no names/accounts/recovery questionnaire or fingerprinting |
| Treat existing ContributorId as a person | Correct its interpretation: it identifies a local research-store lineage, not necessarily a person/device |
| Fit participant effects | Fit session effects and optional lineage effects, labeled honestly; residual experience confounding remains |
| Require 20 independent people with two sessions | Withdraw for anonymous/unverified-linkage collection; use recording milestones and coverage, without claiming equivalent statistical power |
| Use person holdouts and person bootstrap intervals | Use known-lineage/session grouping, label results conditional, and test hidden-dependence sensitivity |
| Reserve genuinely new people automatically | Reserve later recordings and unseen known lineages/texts; do not equate them to verified new people |
| Validate new mappings and composition rules | Keep; remove all known-linked groups from training for mapping/rule holdouts |
| Search and public challenge | Keep as a reproducible model-score task with validation scope and unsupported contexts visible |

## Identity distinction

Kala's ResearchStore already generates a random local ID without asking the user to identify themselves. That code is useful for grouping and withdrawal, but a shared computer may have several users, and one person may have several IDs. Resetting the local store can also create a new ID.

The default revision retains existing consented linkage without introducing new tracking. If only session linkage is available, use session-only mode. Neither mode can establish the number of independent people. Do not infer identity from IP addresses, hardware fingerprints or typing behavior.

## Practical analysis without questions

Use the existing 260-second task, with clear natural-text/probe/coverage labels. Record actual Shift-side behavior, correctness, timing distributions, overlaps, repetitions and interrupted segments. Those are measurements of the task.

Use balanced common tasks, within-session variation, session nuisance effects, regularization and multiple mappings. Keep all known-linked sessions together when splitting data. Limit prolific-lineage influence and report concentration. Repeat the analysis with different weighting and dependence assumptions.

Do not call a fast session an expert, use high accuracy as proof of familiarity, or use an observed Space event to infer which thumb pressed it. Do not normalize away all session speed using WPM and assume that only physical key costs remain. Evaluate any calibration without using the outcomes being tested.

## What remains unmitigated

Without reliable person linkage, unnoticed repeat people can occur in training and testing. Grouping by session or local ID reduces known leakage but cannot rule out hidden leakage. Conditional bootstrap intervals and hypothetical shared-person simulations make assumptions visible; they do not restore a population guarantee.

The model can still produce comparable predicted scores and support exploratory searches. A public model-score challenge can be reproducible without claiming that its winner makes all Bangla users faster. Stronger new-person, experienced-user or causal switching claims require separate evidence, potentially an observed design that does not collect names or questionnaires.

The user-facing collection stays simple: consent, predefined typing tasks, and optional sharing. No experience survey is a prerequisite.

## Revised next steps

The [updated mitigation plan](MITIGATION_PLAN.md) expands these steps into the minimal client data contract, gap mitigations, repository owners and acceptance checks.

1. Freeze the minimal observable-data contract and linkage semantics; retain explicit unknowns.
2. Implement only the necessary client/receiver/research compatibility changes for actions, engine attribution and task/boundary metadata.
3. Complete the observed instrumentation pilot.
4. Collect varied recordings across mappings and composition families; monitor observed coverage and group concentration.
5. Fit session-adjusted models; validate group/text/mapping/rule transfer and mean-time calibration.
6. Publish recording-scope model results, score candidates and search A/D; leave unsupported rules provisional.

The revised 40-session development milestone is an engineering target only. It is not a replacement power calculation for 20 people. No amount of repeated data identifies the unknown number of people automatically.

The general concern about repeated observations crossing training/test partitions is supported by [Chaibub Neto et al. (2019)](https://www.nature.com/articles/s41746-019-0178-x). That study concerns another application domain; its numerical findings are not imported as Bangla evidence. Applying the dependence warning to this study is a methodological inference.

## Validation of this amendment

Reviewed the supplied mitigation text and Kala's ResearchStore source. Updated documentation, reviewed consistency and refreshed artifact hashes. No software tests were rerun, no code changed, and no new empirical result was fitted. The earlier 63-test result remains historical evidence from the preceding review.
