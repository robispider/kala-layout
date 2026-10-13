# Correction: direction of Engram scores

Engram pair and triple-order scores award credit: **higher is better**. This is explicit in
[the mechanics documentation](../../../docs/MECHANICS.md) and in the pair evaluator’s
`score_direction = "higher"`. Triple order also awards credit for preferred sequences.

The prose in the earlier interpretation reports and balance review wrongly treated a
decrease in a lower coverage bound as a cost reduction. The stored numbers were correct,
but those Engram gain/regression statements must be reversed. In particular:

* D-072c558b633d1019 lowers both displayed Engram credit bounds under both fingerings;
  those are regressions on these credit measures. Its 17.66% cross-space SF-rate reduction
  and 15.81% SF-distance reduction under primary fingering remain correct.
* The reviewed D candidate at the 0.5% J1 band raises both credit bounds under both
  fingerings; those changes were incorrectly described as Engram regressions.
* The reviewed A candidate at the 0.1% band raises both credit bounds under primary
  fingering; those were incorrectly described as worsening costs.

Lower coverage bounds are not full comfort scores; their changes also need coverage
and source scope to be considered. A cross-space improvement is not evidence that all
mechanical criteria improve. This correction supersedes the earlier Engram prose and
the claim that the balanced D candidate improved both Engram diagnostics. It does not
change any J1, cross-space SF-rate or SF-distance measurement, any found layout, or the
conclusion that the strict primary J1/movement gate found no success.
