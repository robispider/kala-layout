"""``generate-layout``: run the layout search yourself and compare it with Kala's layouts.

The search is the one that found Kala Goti (style A) and Kala Jhor (style D):
simulated annealing plus iterated local search on the 52-slot problem, scored by
J1 on a 0.5 / 0.5 mix of the Wikipedia and newspaper training texts. It needs no
text download: the keystroke tables it reads are committed under ``results/``.

By default the search starts from scratch (random layouts, your own seed range),
so you can see whether an independent run lands on the same layout. ``--reproduce``
repeats the published run exactly (512 seeds, the published seed range, the polish
from the earlier layouts) and expects the identical layout.

Results go to ``--out`` (default ``work/generate-<style>``, ignored by Git); the
published results are never touched.
"""
from __future__ import annotations

import json
from pathlib import Path

from . import mix
from .challenge import _key_layout
from .crosscheck import score_style
from .paths import PROJECT_ROOT, RESULTS_ROOT, relative_to_project, write_json, write_text
from .phase3 import problem_fixed
from .scoring.model import ANSI_GRID, KeyModel
from .search.problem import load_problem

NAMES = {"A": "Kala Goti", "D": "Kala Jhor"}
PUBLISHED = mix.RESULTS / "search"
FULL_SEEDS = 512


def _differences(mine: dict, published: dict) -> list[tuple[str, tuple, tuple]]:
    return [(symbol, mine[symbol], published[symbol]) for symbol in sorted(mine) if mine[symbol] != published[symbol]]


def compare(style: str, out: Path, weights: dict[str, float]) -> dict:
    problem = load_problem()
    model = KeyModel.from_grid(ANSI_GRID)
    fixed = problem_fixed(problem)
    mine = mix.mixed_best_layout(style, out / "search")
    published = mix.mixed_best_layout(style, PUBLISHED)
    rows = {}
    for corpus in (*weights, *mix.HELDOUT):
        a = score_style(style, mine, corpus, model, fixed)["J1"]
        b = score_style(style, published, corpus, model, fixed)["J1"]
        rows[corpus] = {"yours": a, "published": b}
    train_yours = sum(w * rows[c]["yours"] for c, w in weights.items())
    train_published = sum(w * rows[c]["published"] for c, w in weights.items())
    differing = _differences(mine, published)
    same = not differing
    if same:
        verdict = f"the same layout as {NAMES[style]}"
    elif train_yours < train_published - 1e-9:
        verdict = f"a different layout with LOWER training J1 than {NAMES[style]}: a candidate improvement. Send it to the challenge"
    elif train_yours > train_published + 1e-9:
        verdict = f"a different layout with higher training J1 than {NAMES[style]} (the search did not find the best layout in this run)"
    else:
        verdict = f"a different layout with equal training J1 to {NAMES[style]}"
    return {"style": style, "name": NAMES[style], "same_layout": same, "training_J1": {"yours": train_yours,
            "published": train_published}, "by_text": rows, "keys_that_differ": len(differing),
            "differences": [{"symbol": s, "yours": "/".join(a), "published": "/".join(b)} for s, a, b in differing],
            "verdict": verdict}


def render(result: dict) -> str:
    L = [f"Style {result['style']} ({result['name']})", "",
         f"  {'':28}{'your search':>14}{'published':>14}{'difference':>12}"]
    train = result["training_J1"]
    L.append(f"  {'training J1 (0.5 wiki + 0.5 news)':28}{train['yours']:>14.6f}{train['published']:>14.6f}"
             f"{(train['yours'] / train['published'] - 1) * 100:>+11.4f}%")
    for corpus, r in result["by_text"].items():
        if corpus.endswith("/heldout"):
            L.append(f"  {'held-out ' + corpus.split('/')[0]:28}{r['yours']:>14.6f}{r['published']:>14.6f}"
                     f"{(r['yours'] / r['published'] - 1) * 100:>+11.4f}%")
    L += ["", f"  Result: {result['verdict']}."]
    if result["differences"]:
        shown = ", ".join(f"{d['symbol']} {d['yours']} (published {d['published']})" for d in result["differences"][:8])
        more = f" and {len(result['differences']) - 8} more" if len(result["differences"]) > 8 else ""
        L.append(f"  {result['keys_that_differ']} symbols sit in a different slot: {shown}{more}.")
    return "\n".join(L)


def run(styles=("D",), seeds: int = 32, first_seed: int = mix.FIRST_SEED, workers: int | None = None,
        out: str | Path | None = None, weights: dict[str, float] | None = None, reproduce: bool = False) -> int:
    weights = weights or dict(mix.DEFAULT_WEIGHTS)
    styles = list(styles)
    if reproduce:
        seeds, first_seed, weights = FULL_SEEDS, mix.FIRST_SEED, dict(mix.DEFAULT_WEIGHTS)
    out = Path(out) if out else PROJECT_ROOT / "work" / ("reproduce" if reproduce else "generate-" + "".join(styles))
    out = out if out.is_absolute() else PROJECT_ROOT / out
    if out.resolve() == mix.RESULTS.resolve():
        raise SystemExit("--out must not be results/mix-search: that folder holds the published results")
    print(f"searching style {', '.join(styles)}: {seeds} seeds from {first_seed}, output {relative_to_project(out)}"
          + (" (exact reproduction of the published run)" if reproduce else ""), flush=True)
    mix.run_optimize(styles=styles, weights=weights, seeds=seeds, workers=workers, out=out, first_seed=first_seed,
                     use_earlier=reproduce)
    comparisons = {}
    for style in styles:
        result = compare(style, out, weights)
        comparisons[style] = result
        layout = mix.mixed_best_layout(style, out / "search")
        write_json(out / f"{style}-layout.json", {"style": style, "name": f"my {NAMES[style]} search", "layout":
                                                   _key_layout(layout)})
        print("\n" + render(result))
    write_json(out / "comparison.json", comparisons)
    write_text(out / "COMPARISON.txt", "\n\n".join(render(r) for r in comparisons.values()) + "\n")
    print(f"\nLayout files: {', '.join(relative_to_project(out / f'{s}-layout.json') for s in styles)} "
          "(score them with the challenge scorer, see docs/CHALLENGE.md)")
    return 0 if not reproduce or all(r["same_layout"] for r in comparisons.values()) else 1
