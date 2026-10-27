"""Small contributor-weighted predictors and leakage-safe evaluation.

Numerical routines use only the standard library. These engineering coverage
floors are not power calculations or a justification for layout comparisons.
"""
from collections import Counter, defaultdict
import hashlib
import math
import random
import statistics
import json

VERSION = "usage-fit-v1"
FEATURES = ("distance_u same_key same_finger hand_alternation to_shift_left to_shift_right shift_transition "
            "from_row to_row elapsed_active_seconds session_number target_length repeated_seen frozen_pair_effort "
            "stage_warmup stage_coverage stage_natural2 stage_repeat").split()


def vector(row):
    values = [row[n] for n in FEATURES[:11]]
    values += [row["target_codepoints"], bool(row["previously_seen"] or row["repeat_of"] is not None), row["frozen_pair_effort"]]
    values += [row["stage"] == s for s in ("warmup", "coverage", "natural-2", "anchor-repeat")]
    return [float(v) for v in values]


def grouped_folds(rows, group, folds, seed):
    groups = sorted({r[group] for r in rows}, key=lambda g: hashlib.sha256(f"{seed}:{g}".encode()).hexdigest())
    if len(groups) < folds: raise ValueError("insufficient split groups")
    assignment = {g: i % folds for i, g in enumerate(groups)}
    return [( [r for r in rows if assignment[r[group]] != f],
              [r for r in rows if assignment[r[group]] == f]) for f in range(folds)], assignment


def weights(rows):
    counts = Counter(r["contributor_id"] for r in rows)
    # Mean observation weight = 1; contributors contribute equal total weight.
    return [len(rows) / (len(counts) * counts[r["contributor_id"]]) for r in rows]


def weighted_median(values, ws):
    cumulative = 0
    for v, w in sorted(zip(values, ws)):
        cumulative += w
        if cumulative >= sum(ws) / 2: return v


def solve(matrix, target):
    """Pivoted elimination of the small ridge normal system."""
    a = [row[:] + [y] for row, y in zip(matrix, target)]
    for i in range(len(a)):
        pivot = max(range(i, len(a)), key=lambda k: abs(a[k][i]))
        if abs(a[pivot][i]) < 1e-12: raise ValueError("singular model system")
        a[i], a[pivot] = a[pivot], a[i]
        value = a[i][i]; a[i] = [v / value for v in a[i]]
        for k in range(len(a)):
            if k != i:
                factor = a[k][i]; a[k] = [x - factor*y for x, y in zip(a[k], a[i])]
    return [r[-1] for r in a]


def ridge(rows, penalty=1.0, feature_names=FEATURES):
    vectors, ys, ws = [vector(r) for r in rows], [r["log_down_down_seconds"] for r in rows], weights(rows)
    indices = [FEATURES.index(n) for n in feature_names]
    means = [sum(w*x[j] for w, x in zip(ws, vectors))/sum(ws) for j in indices]
    scales = [math.sqrt(sum(w*(x[j]-mean)**2 for w, x in zip(ws, vectors))/sum(ws)) for j, mean in zip(indices, means)]
    supported = [i for i, scale in enumerate(scales) if scale > 1e-12]
    xs = [[1.0] + [(v[indices[i]]-means[i])/scales[i] for i in supported] for v in vectors]
    n = len(supported) + 1
    matrix = [[sum(w*x[i]*x[j] for w, x in zip(ws, xs)) + (penalty if i == j and i > 0 else 0) for j in range(n)] for i in range(n)]
    target = [sum(w*x[i]*y for w, x, y in zip(ws, xs, ys)) for i in range(n)]
    coefficients = solve(matrix, target)
    return {"intercept": coefficients[0], "features": list(feature_names), "means": means, "scales": scales,
            "coefficients": {name: (coefficients[supported.index(i)+1] if i in supported else None) for i, name in enumerate(feature_names)},
            "unsupported_features": [name for i, name in enumerate(feature_names) if i not in supported], "penalty": penalty}


def predict(model, row):
    values = vector(row)
    return model["intercept"] + sum(model["coefficients"][name] * (values[FEATURES.index(name)]-mean)/scale
                                    for name, mean, scale in zip(model["features"], model["means"], model["scales"])
                                    if model["coefficients"][name] is not None)


def metrics(predictions, seed, bootstrap=500):
    by_person = defaultdict(list)
    for r in predictions: by_person[r["contributor_id"]].append(r)
    person = {}
    for cid, rows in by_person.items():
        person[cid] = {"log_mae": statistics.mean(abs(r["predicted_log"]-r["actual_log"]) for r in rows),
                       "millisecond_mae": statistics.mean(abs(r["predicted_ms"]-r["actual_ms"]) for r in rows),
                       "median_signed_ms_error": statistics.median(r["predicted_ms"]-r["actual_ms"] for r in rows),
                       "mean_signed_log_error": statistics.mean(r["predicted_log"]-r["actual_log"] for r in rows), "rows": len(rows)}
    ids = sorted(person); rng = random.Random(seed)
    estimates = sorted(statistics.mean(person[rng.choice(ids)]["millisecond_mae"] for _ in ids) for _ in range(bootstrap))
    return {"participant_weighted_log_mae": statistics.mean(v["log_mae"] for v in person.values()),
            "participant_weighted_millisecond_mae": statistics.mean(v["millisecond_mae"] for v in person.values()),
            "contributor_bootstrap_95pct_ms_mae": [estimates[int(.025*bootstrap)], estimates[min(bootstrap-1, int(.975*bootstrap))]],
            "bootstrap_unit": "contributor", "contributor_residuals": person}


def evaluate(rows, policy):
    seed, folds = policy["seed"], policy["folds"]
    evaluations, all_predictions = {}, []
    for axis in ("contributor_id", "family"):
        splits, assignment = grouped_folds(rows, axis, folds, seed)
        candidates = defaultdict(list); fold_models = []
        for fold, (train, test) in enumerate(splits):
            if min(len(train), len(test)) < policy["minimum_intervals_per_fold"]:
                return {"status": "insufficient_data", "reason": "fold_interval_floor", "axis": axis}, []
            # No trimming; all normalization and coefficients learn from train.
            ws = weights(train)
            median = weighted_median([r["log_down_down_seconds"] for r in train], ws)
            models = {"additive_ridge": ridge(train, policy["ridge_penalty"]),
                      "frozen_effort_ridge": ridge(train, policy["ridge_penalty"], ["frozen_pair_effort"])}
            fold_models.append({"fold": fold, "train_groups": sorted({r[axis] for r in train}), "test_groups": sorted({r[axis] for r in test}),
                                "training_median_log": median, "models": models})
            for r in test:
                for name in ("training_median", *models):
                    pred = median if name == "training_median" else predict(models[name], r)
                    # Do not hide unstable predictions behind a clipping rule.
                    if abs(pred) > 50: return {"status": "numerical_failure", "reason": "unstable_prediction"}, []
                    row = {k: r[k] for k in ("package_sha256", "contributor_id", "session_id", "prompt_order", "from_seq", "to_seq", "to_position", "stage", "geometry", "to_shift_left", "to_shift_right")}
                    row.update(axis=axis, model=name, fold=fold, actual_log=r["log_down_down_seconds"], predicted_log=pred,
                               actual_ms=1000*r["down_down_seconds"], predicted_ms=1000*math.exp(pred))
                    candidates[name].append(row); all_predictions.append(row)
        evaluations[axis] = {"split_assignment": assignment, "fold_models": fold_models, "metrics": {}}
        for name, predictions in candidates.items():
            report = metrics(predictions, seed, policy["bootstrap_repetitions"])
            report["strata"] = {}
            for field in ("to_position", "stage", "geometry", "to_shift_left", "to_shift_right"):
                grouped = defaultdict(list)
                for r in predictions: grouped[str(r[field])].append(r)
                report["strata"][field] = {value: {"rows": len(group), "contributors": len({r['contributor_id'] for r in group}),
                    "log_mae": statistics.mean(abs(r['predicted_log']-r['actual_log']) for r in group),
                    "millisecond_mae": statistics.mean(abs(r['predicted_ms']-r['actual_ms']) for r in group)} for value, group in sorted(grouped.items())}
            evaluations[axis]["metrics"][name] = report
    if any(report["metrics"]["additive_ridge"]["participant_weighted_log_mae"] >=
           report["metrics"]["training_median"]["participant_weighted_log_mae"] for report in evaluations.values()):
        return {"status": "validation_failed", "reason": "does_not_beat_median_on_both_holdout_axes", "evaluations": evaluations}, all_predictions
    support = defaultdict(set)
    for r in rows:
        key = json.dumps([r["geometry"], r["from_position"], r["to_position"], r["from_shift_left"], r["from_shift_right"], r["to_shift_left"], r["to_shift_right"]], separators=(",", ":"))
        support[key].add(r["contributor_id"])
    by_person = defaultdict(list)
    for r in rows: by_person[r["contributor_id"]].append(r)
    rng = random.Random(seed); ids = sorted(by_person); bootstrap_models, bootstrap_ids = [], []
    for _ in range(policy["cost_model_bootstrap_repetitions"]):
        sampled = [rng.choice(ids) for _ in ids]; bootstrap_ids.append(sampled)
        sample = [dict(r, contributor_id=f"draw-{draw}") for draw, cid in enumerate(sampled) for r in by_person[cid]]
        bootstrap_models.append(ridge(sample, policy["ridge_penalty"]))
    return {"status": "experimental_fit", "evaluations": evaluations,
            "final_interval_model": ridge(rows, policy["ridge_penalty"]),
            "support_contributors": {k: len(v) for k,v in sorted(support.items())},
            "bootstrap_models": bootstrap_models, "bootstrap_contributor_draws": bootstrap_ids,
            "limitations": ["Engineering coverage floors do not establish statistical adequacy.", "No layout effect, comfort estimate or unseen-layout transfer claim.",
                            "Prompt-family validation requires reviewed source-work and near-duplicate identities.",
                            "Per-contributor residuals are conditional diagnostics; no observed finger choices."]}, all_predictions


def correction_baseline(rows, policy):
    """Separate observed native-correction probability; no latent symbol-error claim."""
    rows = [r for r in rows if r["decision"] == "accepted" and r["correction_observed"] is not None]
    if len({r["contributor_id"] for r in rows}) < policy["minimum_contributors"] or sum(r["correction_observed"] for r in rows) < policy["minimum_corrections"]:
        return {"status": "insufficient_data", "target": "observed_correction_action"}
    splits, assignment = grouped_folds(rows, "contributor_id", policy["folds"], policy["seed"])
    results = defaultdict(list)
    calibration = defaultdict(list)
    for train, test in splits:
        ws = weights(train)
        probability = (sum(w*r["correction_observed"] for w, r in zip(ws, train)) + .5) / (sum(ws) + 1)
        for r in test:
            y = r["correction_observed"]
            results[r["contributor_id"]].append(((probability-y)**2, -(y*math.log(probability)+(1-y)*math.log1p(-probability))))
            calibration[min(9, int(probability*10))].append((probability, y))
    return {"status": "experimental_baseline", "target": "observed_correction_action", "split_assignment": assignment,
            "participant_weighted_brier": statistics.mean(statistics.mean(v[0] for v in rows) for rows in results.values()),
            "participant_weighted_log_loss": statistics.mean(statistics.mean(v[1] for v in rows) for rows in results.values()),
            "calibration": [{"bin": k, "count": len(v), "mean_probability": statistics.mean(x[0] for x in v), "observed_fraction": statistics.mean(x[1] for x in v)} for k,v in sorted(calibration.items())],
            "limitation": "Native correction-action incidence is not symbol error probability; no composition replacement is counted as a correction."}
