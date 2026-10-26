"""Command-line interface: ``bangla-dh <command>`` (or ``python -m bangla_dh``)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .colemak.analysis import perform_analysis, text_report
from .colemak.frequency import FreqAnalysis, load_char_freqs, load_frequency_file
from .colemak.keyboard import load_layout
from .colemak.switching import compare_layouts, load_overrides


def _reproduce(args) -> int:
    from .reproduce import RESULTS, run, write

    record = run()
    out = Path(args.out) if args.out else RESULTS
    for path in write(record, out):
        print(path)
    for name, ok in record["acceptance"].items():
        print(f"{'PASS' if ok else 'FAIL'}  {name}")
    return 0 if record["accepted"] else 1


def _analyze(args) -> int:
    layout = load_layout(args.layout, *args.config)
    char_freqs, bigram_freqs = load_frequency_file(layout.alphabet(), args.freq)
    results = perform_analysis(layout, char_freqs, bigram_freqs)
    if args.format == "json":
        brief = results.brief()
        brief.update(results.effort_totals())
        print(json.dumps(brief, indent=2, ensure_ascii=False))
    else:
        if args.format in ("text", "all"):
            sys.stdout.write(text_report(results, args.bigrams, args.bigrams))
        if args.format in ("brief", "all"):
            d = results.brief()["display"]
            print(f"{layout.name}  {layout.keyboard_type}  base {d['base_effort']}  sfb {d['same_finger_bigram_percent']}"
                  f"  bigram {d['bigram_penalty']}  total {d['total_effort']}")
    return 0


def _switching(args) -> int:
    old = load_layout(args.old_layout, args.old_config)
    new = load_layout(args.new_layout, args.new_config)
    freqs = load_char_freqs(old.alphabet(), Path(args.freq).read_text(encoding="utf-8"))
    result = compare_layouts(old, new, freqs, load_overrides(args.overrides) if args.overrides else None)
    for k in result.keys:
        if k.score is not None:
            print(f"{k.char}:  {k.movement:f}  {k.freq:f}  {k.freq_cost:f}  {k.effort_ratio:f}  {k.score:f}")
    print(f"\nkeys moved {result.keys_moved} (new finger {result.keys_moved_finger}), "
          f"sum m {result.keys_moved_index:.2f}, d {result.switching_difficulty:.3f}")
    return 0


def _freq_analysis(args) -> int:
    analysis = FreqAnalysis(args.alphabet.upper(), args.max_unicode)
    analysis.analyze(Path(args.file).read_text(encoding="utf-8"))
    if args.normalized:
        analysis.normalize()
    sys.stdout.write(analysis.frequency_file_text(args.normalized))
    return 0


def _effort_grid(args) -> int:
    from .geometry.analyzer_config import model_config_text
    from .geometry.effort_model import EffortParams, effort_grid, traditional_fingers
    from .geometry.keyboards import KEYBOARDS
    from .reproduce import FROZEN_DISTANCE_SCALE

    keyboard = KEYBOARDS[args.keyboard]()
    params = EffortParams(distance_scale=args.distance_scale or FROZEN_DISTANCE_SCALE)
    if args.config:
        sys.stdout.write(model_config_text(keyboard, params, fingers=args.fingers, bottom=args.bottom,
                                           decimals=args.decimals))
        return 0
    assignment = traditional_fingers(keyboard) if args.fingers == "traditional" else None
    grid = effort_grid(keyboard, params, assignment)
    for row in sorted({k.row for k in keyboard.keys}):
        cells = [f"{k.name}={grid[k.name].effort:.{args.decimals or 2}f}/{grid[k.name].finger}"
                 for k in keyboard.keys if k.row == row]
        print("  ".join(cells))
    return 0


def _calibrate(args) -> int:
    from .geometry.calibrate import scan_distance_scale
    from .reference import load_published

    scan = scan_distance_scale(load_published(), start=args.start, stop=args.stop, step=args.step)
    print(json.dumps({k: v for k, v in scan.items() if k != "curve"}, indent=2))
    return 0


def _verify_reference(args) -> int:
    from .reference import verify_upstream, verify_vendored

    problems = verify_vendored()
    print("vendored resources: " + ("ok" if not problems else "; ".join(problems)))
    upstream = verify_upstream()
    print("upstream analyzer source: " + ("ok" if not upstream else "; ".join(upstream)))
    return 1 if problems else 0


def _fetch_upstream(args) -> int:
    from .reference import fetch_upstream

    problems = fetch_upstream()
    print("upstream analyzer source: " + ("verified" if not problems else "; ".join(problems)))
    return 1 if problems else 0


def _inventory(args) -> int:
    from .kala_data import inventory

    print(json.dumps(inventory(), indent=2, ensure_ascii=False))
    return 0


def _fetch_data(args) -> int:
    from . import datasets

    datasets.fetch(args.package, workers=args.workers, mirror=args.mirror)
    return 0


def _prepare_data(args) -> int:
    from . import datasets

    datasets.assemble(args.package)
    return 0


def _verify_data(args) -> int:
    from . import datasets

    return 0 if datasets.verify(args.package) else 1


def _audit_usage_data(args) -> int:
    from .usage_metric import InvalidData, run
    from .paths import DATA, RESULTS_ROOT

    try:
        record, paths = run(Path(args.dataset) if args.dataset else DATA / "usage-metric-dataset",
                            Path(args.out) if args.out else RESULTS_ROOT / "usage-metric-audit-v1")
    except (InvalidData, OSError, ValueError, KeyError, TypeError):
        print("Unable to audit: missing or malformed dataset manifest, or invalid output path.", file=sys.stderr)
        return 1
    for path in paths:
        print(path)
    print(f"{record['status']}: {record['valid_sessions']}/{record['manifest_entries']} packages; "
          f"{record['contributors']} contributors; model_ready=False")
    return 1 if record["errors"] else 0


def _lock_datasets(args) -> int:
    from . import datasets

    print(datasets.write_lock(args.checkout, args.commit, assembled=args.assembled))
    return 0


def _print_paths(paths) -> int:
    for path in paths:
        print(path)
    return 0


def _build_inventory(args) -> int:
    from .phase2 import run_inventory

    return _print_paths(run_inventory())


def _build_corpus(args) -> int:
    from .phase2 import run_corpus

    return _print_paths(run_corpus())


def _compute_frequency(args) -> int:
    from .phase2 import run_frequency

    return _print_paths(run_frequency())


def _evaluate_phase2(args) -> int:
    from .phase2_report import run_and_write

    return run_and_write()


def _build_problem(args) -> int:
    from .phase3 import run_problem

    return _print_paths(run_problem())


def _style_frequency(args) -> int:
    from .phase3 import run_style_frequency

    return _print_paths(run_style_frequency(workers=args.workers))


def _optimize(args) -> int:
    from .phase3 import run_optimize

    return _print_paths(run_optimize(styles=args.styles, seeds=args.seeds, sa_steps=args.steps,
                                     ils_iterations=args.ils, workers=args.workers))


def _evaluate_phase3(args) -> int:
    from .phase3_report import run_and_write

    return run_and_write()


def _crosscheck_build(args) -> int:
    from .crosscheck import run_build

    return _print_paths(run_build(workers=args.workers, skip_corpus=args.skip_corpus))


def _crosscheck_optimize(args) -> int:
    from .crosscheck import run_optimize

    return _print_paths(run_optimize(seeds=args.seeds, workers=args.workers))


def _evaluate_crosscheck(args) -> int:
    from .crosscheck import run_and_write

    return run_and_write(report_only=args.report_only)


def _certify(args) -> int:
    from .phase4 import run_certify

    steps = {"cpsat", "subproblems", "layers", "exchange"} - set(args.skip or [])
    return _print_paths(run_certify(styles=args.styles, steps=steps))


def _certify_lp(args) -> int:
    from .phase4 import run_certify_lp

    return _print_paths(run_certify_lp(styles=args.styles))


def _sensitivity(args) -> int:
    from .phase4 import run_sensitivity

    return _print_paths(run_sensitivity(workers=args.workers))


def _evaluate_phase4(args) -> int:
    from .phase4_report import run_and_write

    return run_and_write(verify=not args.no_verify, report_only=args.report_only)


def _mix_optimize(args) -> int:
    from .mix import parse_weights, run_optimize

    return _print_paths(run_optimize(styles=args.styles, weights=parse_weights(args.weights), seeds=args.seeds,
                                     sa_steps=args.steps, ils_iterations=args.ils, workers=args.workers))


def _challenge_kit(args) -> int:
    from .challenge import run_build

    return _print_paths(run_build(leaderboard=args.leaderboard))


def _challenge_verify(args) -> int:
    from .challenge import run_verify

    return run_verify(args.files, diagnostics=args.diagnostics)


def _kala_export(args) -> int:
    from .kala_export import run_export

    return _print_paths(run_export(top=args.top, fuzz_count=args.fuzz))


def _generate_layout(args) -> int:
    from .generate import run
    from .mix import parse_weights

    return run(styles=args.style, seeds=args.seeds, first_seed=args.first_seed, workers=args.workers, out=args.out,
               weights=parse_weights(args.weights), reproduce=args.reproduce)


def _leaderboard(args) -> int:
    from .leaderboard import run

    return run(args.files or None, check=args.check, diagnostics=args.diagnostics)


def _check_results(args) -> int:
    from .reproduction import check_results, lock_results

    if args.lock:
        print(lock_results())
        return 0
    return 0 if check_results(args.group) else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="bangla-dh", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("audit-usage-data", help="independently audit received typing-study packages; no model fitting")
    p.add_argument("--dataset", help="dataset directory (default data/usage-metric-dataset)")
    p.add_argument("--out", help="report directory inside the repository (default results/usage-metric-audit-v1)")
    p.set_defaults(func=_audit_usage_data)

    p = sub.add_parser("reproduce-colemak", help="Phase 1: reproduce the published Colemak Mod-DH results")
    p.add_argument("--out", help="output directory (default results/phase1)")
    p.set_defaults(func=_reproduce)

    p = sub.add_parser("analyze", help="score a layout (port of KeyboardAnalysis)")
    p.add_argument("--layout", required=True)
    p.add_argument("--config", required=True, nargs="+")
    p.add_argument("--freq", required=True)
    p.add_argument("--format", choices=["brief", "text", "json", "all"], default="all")
    p.add_argument("--bigrams", type=int, default=10, help="same/neighbour-finger bigrams listed")
    p.set_defaults(func=_analyze)

    p = sub.add_parser("switching", help="switching difficulty between layouts (port of KeyboardCompare)")
    p.add_argument("--freq", required=True)
    p.add_argument("--overrides")
    p.add_argument("old_layout")
    p.add_argument("old_config")
    p.add_argument("new_layout")
    p.add_argument("new_config")
    p.set_defaults(func=_switching)

    p = sub.add_parser("freq-analysis", help="character/bigram counts of a text (port of FreqAnalysis)")
    p.add_argument("--alphabet", default="ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    p.add_argument("--max-unicode", type=int, default=-1)
    p.add_argument("--normalized", action="store_true")
    p.add_argument("file")
    p.set_defaults(func=_freq_analysis)

    p = sub.add_parser("effort-grid", help="reconstructed effort grid of a keyboard")
    p.add_argument("--keyboard", choices=["iso", "ansi", "matrix"], default="ansi")
    p.add_argument("--fingers", choices=["optimal", "traditional"], default="optimal")
    p.add_argument("--distance-scale", type=float)
    p.add_argument("--decimals", type=int)
    p.add_argument("--config", action="store_true", help="print as an analyzer config file")
    p.add_argument("--bottom", choices=["angle", "std"], default="std", help="bottom-row mapping for --config")
    p.set_defaults(func=_effort_grid)

    p = sub.add_parser("calibrate-grid", help="scan P_d against the published grids")
    p.add_argument("--start", type=float, default=0.9)
    p.add_argument("--stop", type=float, default=1.3)
    p.add_argument("--step", type=float, default=0.0005)
    p.set_defaults(func=_calibrate)

    sub.add_parser("verify-reference", help="check pinned reference hashes").set_defaults(func=_verify_reference)
    sub.add_parser("fetch-upstream", help="clone the original analyzer at the pinned commit").set_defaults(func=_fetch_upstream)
    sub.add_parser("inventory-kala", help="list the vendored Kala inputs (data/kala) with their SHA-256"
                   ).set_defaults(func=_inventory)

    packages = ["wikipedia", "newspaper", "bard", "all"]
    p = sub.add_parser("fetch-data", help="download the public datasets (ban-dataset-collection) and verify SHA-256")
    p.add_argument("--package", nargs="+", choices=packages, default=["all"])
    p.add_argument("--workers", type=int, default=4, help="parallel downloads (default 4)")
    p.add_argument("--from", dest="mirror", help="copy the chunks from a local checkout of the collection instead")
    p.set_defaults(func=_fetch_data)
    p = sub.add_parser("prepare-data", help="assemble the downloaded chunks and check them against the lock")
    p.add_argument("--package", nargs="+", choices=packages, default=["all"])
    p.set_defaults(func=_prepare_data)
    p = sub.add_parser("verify-data", help="re-check downloaded and assembled data against the lock")
    p.add_argument("--package", nargs="+", choices=packages, default=["all"])
    p.set_defaults(func=_verify_data)
    p = sub.add_parser("lock-datasets", help="maintainer: write data/datasets.lock.json from a checkout")
    p.add_argument("checkout")
    p.add_argument("commit")
    p.add_argument("--assembled", action="store_true", help="also record the assembled files' content hashes")
    p.set_defaults(func=_lock_datasets)

    sub.add_parser("build-inventory", help="Phase 2: Bangla symbol inventory from Kala's alphabet, validated"
                   ).set_defaults(func=_build_inventory)
    sub.add_parser("build-corpus", help="Phase 2: check the prepared Wikipedia against the lock and write data/corpus"
                   ).set_defaults(func=_build_corpus)
    sub.add_parser("compute-frequency", help="Phase 2: token tables and unit/bigram frequencies"
                   ).set_defaults(func=_compute_frequency)
    sub.add_parser("evaluate-phase2", help="Phase 2: scorer checks, baselines and report"
                   ).set_defaults(func=_evaluate_phase2)

    sub.add_parser("build-problem", help="Phase 3: the v1 problem file (slots, fixed keys, symbols per style)"
                   ).set_defaults(func=_build_problem)
    p = sub.add_parser("style-frequency", help="Phase 3: keystroke tables of the vowel-entry styles A-D")
    p.add_argument("--workers", type=int)
    p.set_defaults(func=_style_frequency)
    p = sub.add_parser("optimize", help="Phase 3: seeded search (annealing + iterated local search), objective J1")
    p.add_argument("--styles", nargs="+", choices=["A", "B", "C", "D"], default=["A", "B", "C", "D"])
    p.add_argument("--seeds", type=int, help="runs per style (default 64)")
    p.add_argument("--steps", type=int, help="annealing steps per run (default 1,000,000)")
    p.add_argument("--ils", type=int, help="iterated local search iterations per run (default 1000)")
    p.add_argument("--workers", type=int)
    p.set_defaults(func=_optimize)
    sub.add_parser("evaluate-phase3", help="Phase 3: checks, J1 baselines, held-out comparison and report"
                   ).set_defaults(func=_evaluate_phase3)

    p = sub.add_parser("crosscheck-build", help="Phase 3 cross-check: news corpora, frequencies, keystroke tables")
    p.add_argument("--workers", type=int)
    p.add_argument("--skip-corpus", action="store_true", help="reuse the built corpus files")
    p.set_defaults(func=_crosscheck_build)
    p = sub.add_parser("crosscheck-optimize", help="Phase 3 cross-check: the Phase 3 search on news text")
    p.add_argument("--seeds", type=int, help="runs per style (default from data/crosscheck-v1.json)")
    p.add_argument("--workers", type=int)
    p.set_defaults(func=_crosscheck_optimize)
    p = sub.add_parser("evaluate-crosscheck", help="Phase 3 cross-check: scores, every baseline, checks and report")
    p.add_argument("--report-only", action="store_true", help="rewrite the report from crosscheck.json")
    p.set_defaults(func=_evaluate_crosscheck)

    p = sub.add_parser("certify", help="Phase 4: integer model, lower bounds, CP-SAT and exchange certificates")
    p.add_argument("--styles", nargs="+", choices=["A", "B", "C", "D"], default=["A", "B", "C", "D"])
    p.add_argument("--skip", nargs="+", choices=["cpsat", "subproblems", "layers", "exchange"],
                   help="leave out these (slow) steps")
    p.set_defaults(func=_certify)
    p = sub.add_parser("certify-lp", help="Phase 4: cell LP bound (PDLP), certified from its duals in exact arithmetic")
    p.add_argument("--styles", nargs="+", choices=["A", "B", "C", "D"], default=["A", "B", "C", "D"])
    p.set_defaults(func=_certify_lp)
    p = sub.add_parser("sensitivity", help="Phase 4: J1 under sampled model parameters, regret of re-optimizing")
    p.add_argument("--workers", type=int)
    p.set_defaults(func=_sensitivity)
    p = sub.add_parser("evaluate-phase4", help="Phase 4: independent checks, report and run manifest")
    p.add_argument("--no-verify", action="store_true", help="skip the independent verifier on the training split")
    p.add_argument("--report-only", action="store_true", help="rewrite the report from phase4.json")
    p.set_defaults(func=_evaluate_phase4)

    p = sub.add_parser("mix-optimize", help="the Phase 3 search on a weighted mix of training texts (Wikipedia + news)")
    p.add_argument("--styles", nargs="+", choices=["A", "B", "C", "D"], default=["A", "D"])
    p.add_argument("--weights", nargs="+", metavar="SPLIT=W",
                   help="training splits and weights, normalized to sum to one "
                        "(default bnwiki/train=0.5 newspaper/train=0.5)")
    p.add_argument("--seeds", type=int, default=256, help="search runs per style (default 256)")
    p.add_argument("--steps", type=int, help="annealing steps per run (default 1,000,000)")
    p.add_argument("--ils", type=int, help="iterated local search iterations per run (default 1000)")
    p.add_argument("--workers", type=int)
    p.set_defaults(func=_mix_optimize)

    p = sub.add_parser("check-results", help="compare the results on disk with the published ones (results/reproduction.lock.json)")
    p.add_argument("--group", nargs="+", help="only groups whose name contains one of these words (e.g. search tables)")
    p.add_argument("--lock", action="store_true", help="maintainer: record the current results as the published ones")
    p.set_defaults(func=_check_results)
    p = sub.add_parser("generate-layout", help="run the layout search yourself and compare with Kala Goti / Kala Jhor")
    p.add_argument("--style", nargs="+", choices=["A", "D"], default=["D"], help="A = Kala Goti, D = Kala Jhor")
    p.add_argument("--seeds", type=int, default=32, help="independent search runs per style (default 32; the published run used 512)")
    p.add_argument("--first-seed", type=int, default=20261101, help="first random seed; change it to explore other runs")
    p.add_argument("--workers", type=int, help="processes (default: CPUs - 4, at most 24)")
    p.add_argument("--out", help="output folder inside the repository (default work/generate-<style>)")
    p.add_argument("--weights", nargs="+", metavar="SPLIT=W", help="training mix (default bnwiki/train=0.5 newspaper/train=0.5)")
    p.add_argument("--reproduce", action="store_true",
                   help="repeat the published run exactly (512 seeds, published seeds, polish from the earlier layouts)")
    p.set_defaults(func=_generate_layout)
    p = sub.add_parser("challenge-kit", help="standalone scorer for people to challenge the A and D layouts")
    p.add_argument("--leaderboard", help="URL of the leaderboard / submission page, written into the guides")
    p.set_defaults(func=_challenge_kit)
    p = sub.add_parser("leaderboard", help="score every layout file in submissions/ and write the leaderboard")
    p.add_argument("files", nargs="*", help="check these files instead of all of submissions/")
    p.add_argument("--check", action="store_true", help="only validate and score (used by pull requests)")
    p.add_argument("--diagnostics", metavar="DIR", help="optional separate experimental report; no ranking effect")
    p.set_defaults(func=_leaderboard)
    p = sub.add_parser("challenge-verify", help="re-check challenge layout files with the project's scorers")
    p.add_argument("files", nargs="+")
    p.add_argument("--diagnostics", metavar="DIR", help="optional separate experimental report; no scoring effect")
    p.set_defaults(func=_challenge_verify)
    p = sub.add_parser("kala-export", help="the A and D layouts as Kala layout files (Kala Goti, Kala Jhor)")
    p.add_argument("--top", type=int, default=200_000, help="held-out word types typed per text (default 200,000)")
    p.add_argument("--fuzz", type=int, default=20_000, help="random key sequences per layout (default 20,000)")
    p.set_defaults(func=_kala_export)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)
