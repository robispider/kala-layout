"""Phase 1: reproduce the published Colemak Mod-DH calculations and freeze the
regression baseline. ``run`` returns a machine-readable record; ``write``
stores it with a Markdown report under ``results/phase1``.
"""
from __future__ import annotations

import datetime as _dt
import json
import platform
import subprocess
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from . import __version__
from .colemak.analysis import perform_analysis
from .colemak.frequency import load_bigram_freqs, load_char_freqs, load_frequency_file
from .colemak.javacompat import java_format_fixed
from .colemak.keyboard import apply_config, load_layout, parse_layout
from .colemak.switching import ExperienceCurve, compare_layouts, load_overrides
from .geometry.analyzer_config import model_config_text
from .geometry.calibrate import compare_grids, config_grid_consistency, scan_distance_scale, summarize
from .geometry.effort_model import EffortParams, effort_grid, traditional_fingers
from .geometry.keyboards import KEYBOARDS, ansi_staggered, iso_staggered
from .kala_data import inventory
from .reference import (LOCK_FILE, PROJECT_ROOT, PUBLISHED, load_published, resource, sha256_file,
                        verify_upstream, verify_vendored)

FROZEN_DISTANCE_SCALE = 1.12
RESULTS = PROJECT_ROOT / "results" / "phase1"


def _half_up(value: float, decimals: int) -> str:
    return format(Decimal(repr(value)).quantize(Decimal(1).scaleb(-decimals), rounding=ROUND_HALF_UP), "f")


def _analyze(layout_name: str, config_paths, freq: str = "freq/en_books.freq", layout_dir: str = "layout_full"):
    layout = load_layout(resource(f"{layout_dir}/{layout_name}.keyb"), *config_paths)
    char_freqs, bigram_freqs = load_frequency_file(layout.alphabet(), resource(freq))
    return perform_analysis(layout, char_freqs, bigram_freqs)


def comparison_table(published: dict) -> dict:
    table = published["comparison_table"]
    rows, matched = [], 0
    for row in table["rows"]:
        brief = _analyze(row["layout"], [resource("config/" + row["config"])]).brief()
        display = brief["display"]
        reproduced = [display["base_effort"], display["same_finger_bigram_percent"],
                      display["bigram_penalty"], display["total_effort"]]
        ok = reproduced == row["values"]
        matched += ok
        rows.append({"label": row["label"], "config": row["published_config_name"], "published": row["values"],
                     "reproduced": reproduced, "match": ok,
                     "full_precision": {k: brief[k] for k in ("base_effort", "same_finger_bigram_percent",
                                                               "bigram_penalty", "total_effort")}})
    return {"rows": rows, "rows_matched": matched, "rows_total": len(rows),
            "values_matched": sum(a == b for r in rows for a, b in zip(r["published"], r["reproduced"])),
            "values_total": 4 * len(rows)}


def switching_table(published: dict) -> dict:
    table = published["switching_difficulty_table"]
    layout_dir = table["layout_directory"]
    base_config = resource("config/" + table["base_config"])
    freq_text = resource(table["frequency_file"]).read_text(encoding="utf-8")
    rows, matched = [], 0
    for row in table["rows"]:
        old = load_layout(resource(f"{layout_dir}/{table['base_layout']}.keyb"), base_config)
        new = load_layout(resource(f"{layout_dir}/{row['layout']}.keyb"),
                          resource("config/" + row.get("config", table["base_config"])))
        overrides = load_overrides(resource("config/" + row["overrides"])) if "overrides" in row else None
        result = compare_layouts(old, new, load_char_freqs(old.alphabet(), freq_text), overrides)
        without_ratio = sum(k.movement * k.freq_cost for k in result.keys if k.freq_cost is not None)
        reproduced = [result.keys_moved_finger, result.keys_moved, _half_up(result.keys_moved_index, 2),
                      int(_half_up(result.switching_difficulty, 0))]
        ok = reproduced == row["values"]
        matched += ok
        entry = {"label": row["label"], "published": row["values"], "reproduced": reproduced, "match": ok,
                 "switching_difficulty": result.switching_difficulty,
                 "switching_difficulty_without_effort_ratio": without_ratio,
                 "movement_counts": result.counts}
        if not ok and int(_half_up(without_ratio, 0)) == row["values"][3] and reproduced[:3] == row["values"][:3]:
            entry["explanation"] = ("Published d equals the model without the S2/S1 effort ratio, i.e. this cell "
                                    "predates the 2021-03-27 model update that added the ratio.")
        rows.append(entry)
    return {"rows": rows, "rows_matched": matched, "rows_total": len(rows),
            "rows_explained": sum("explanation" in r for r in rows)}


def experience_curve(published: dict) -> dict:
    curve = ExperienceCurve(published["experience_curve_table"]["b"])
    rows = []
    for row in published["experience_curve_table"]["rows"]:
        value = curve.integrated_cost(float(row["f_percent"]))
        rows.append({"f_percent": row["f_percent"], "published": row["C_f"], "reproduced": _half_up(value, 2),
                     "value": value, "match": _half_up(value, 2) == row["C_f"]})
    # Worked example of the Bangla-DH specification (section 2.4), rounded exponent 0.678.
    rounded = 5 ** 0.678 / 0.678
    return {"p": curve.p, "rows": rows, "rows_matched": sum(r["match"] for r in rows),
            "specification_example": {"f": 5, "m": 0.5, "effort_ratio": 1.2,
                                      "C_f_rounded_exponent": rounded, "D_i_rounded_exponent": 0.5 * rounded * 1.2,
                                      "C_f_exact_exponent": curve.integrated_cost(5.0),
                                      "D_i_exact_exponent": 0.5 * curve.integrated_cost(5.0) * 1.2}}


def effort_grid_reconstruction(published: dict) -> dict:
    scan = scan_distance_scale(published)
    params = EffortParams(distance_scale=FROZEN_DISTANCE_SCALE)
    lo, hi = scan["widest_best_interval"]
    return {"frozen_distance_scale": FROZEN_DISTANCE_SCALE,
            "frozen_within_best_interval": lo <= FROZEN_DISTANCE_SCALE <= hi,
            "scan": {k: v for k, v in scan.items() if k != "curve"},
            "at_frozen_value": summarize(compare_grids(published, params)),
            "published_config_vs_image": config_grid_consistency(published, resource),
            "alternative_choices": alternative_choices(published),
            "curve": scan["curve"]}


def alternative_choices(published: dict) -> list[dict]:
    """Best fit of each rejected modelling choice, each at its own best P_d."""
    variants = [("frozen model", EffortParams()),
                ("activation box of half-width 0.3 (margin 0.2)", EffortParams(activation_margin=0.2)),
                ("right-hand resting offsets not mirrored", EffortParams(mirror_right_displacement=False)),
                ("no home-key rule", EffortParams(home_key_is_rest=False))]
    out = []
    for label, params in variants:
        scan = scan_distance_scale(published, params, start=0.8, stop=1.5, step=0.001)
        out.append({"choice": label, "best_matches": scan["best_matches"], "scored_keys": scan["scored_keys"],
                    "best_intervals": scan["best_intervals"]})
    return out


def model_grid_sensitivity(published: dict) -> dict:
    """Re-run the ergonomic/traditional comparison rows on unrounded model grids."""
    params = EffortParams(distance_scale=FROZEN_DISTANCE_SCALE)
    iso = iso_staggered()
    configs = {
        "effort_ergonomic_config.dat": model_config_text(iso, params, fingers="optimal", bottom="angle"),
        "effort_traditional_config.dat": model_config_text(iso, params, fingers="traditional", bottom="std"),
    }
    rows = []
    for row in published["comparison_table"]["rows"]:
        if row["config"] not in configs:
            continue
        layout = parse_layout(resource(f"layout_full/{row['layout']}.keyb").read_text(encoding="utf-8"), row["layout"])
        apply_config(layout, configs[row["config"]])
        char_freqs, bigram_freqs = load_frequency_file(layout.alphabet(), resource("freq/en_books.freq"))
        model_brief = perform_analysis(layout, char_freqs, bigram_freqs).brief()
        rows.append({"label": row["label"], "config": row["published_config_name"],
                     "published_total": row["values"][3], "model_grid_total": java_format_fixed(model_brief["total_effort"], 3),
                     "model_grid_base": java_format_fixed(model_brief["base_effort"], 3)})
    published_rank = [r["label"] + "/" + r["config"] for r in sorted(rows, key=lambda r: float(r["published_total"]))]
    model_rank = [r["label"] + "/" + r["config"] for r in sorted(rows, key=lambda r: float(r["model_grid_total"]))]
    return {"distance_scale": FROZEN_DISTANCE_SCALE, "rows": rows,
            "published_order": published_rank, "model_grid_order": model_rank,
            "order_preserved": published_rank == model_rank, "generated_configs": configs}


def caseless_script_check() -> dict:
    """Show how the original analyzer treats a caseless script such as Bangla."""
    layout = parse_layout("ক া ি\n", "bangla-probe")
    freq_text = "ক 50\nা 30\nি 20\nকা 10\n"
    char_freqs = load_char_freqs(layout.alphabet(), freq_text)
    bigram_freqs = load_bigram_freqs(layout.alphabet(), freq_text)
    for key in layout.keys:
        key.effort = 1.0
    results = perform_analysis(layout, char_freqs, bigram_freqs)
    return {"layout_alphabet": layout.alphabet(), "key_chars": [k.chars for k in layout.keys],
            "duplicate_warnings": layout.duplicate_letters(),
            "base_effort_all_keys_effort_1": results.effort_totals()["base"],
            "expected_without_quirk": 1.0,
            "finding": ("Character.isAlphabetic is true for Bangla letters and vowel signs, which are neither upper- "
                        "nor lower-case, so Key.kt 'shifts' each to itself: every key holds its character twice and "
                        "base effort is counted twice. The original tool cannot score Bangla unmodified; Phase 2 "
                        "uses a Bangla-aware loader instead.")}


def _git(*args: str) -> str:
    try:
        return subprocess.run(["git", "-C", str(PROJECT_ROOT), *args], capture_output=True, text=True,
                              check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


def run() -> dict:
    published = load_published()
    vendored_problems = verify_vendored()
    upstream_problems = verify_upstream()
    record = {
        "phase": 1,
        "title": "Reproduction of the published Colemak Mod-DH model",
        "manifest": {
            "generated_utc": _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat(),
            "bangla_dh_version": __version__,
            "python": sys.version.split()[0], "platform": platform.platform(),
            "kala_commit": _git("rev-parse", "HEAD"), "working_tree_clean": _git("status", "--porcelain", ".") == "",
            "inputs": {"sources.lock.json": sha256_file(LOCK_FILE), "colemak_dh_published.json": sha256_file(PUBLISHED)},
            "parameters": {"frequency_file": "freq/en_books.freq", "layout_directory": "layout_full",
                           "distance_scale": FROZEN_DISTANCE_SCALE, "experience_curve_b": 0.8},
        },
        "reference_integrity": {"vendored_resources_ok": not vendored_problems, "vendored_problems": vendored_problems,
                                "upstream_source_ok": not upstream_problems, "upstream_problems": upstream_problems},
        "comparison_table": comparison_table(published),
        "switching_difficulty_table": switching_table(published),
        "experience_curve": experience_curve(published),
        "effort_grid": effort_grid_reconstruction(published),
        "model_grid_sensitivity": model_grid_sensitivity(published),
        "caseless_script_check": caseless_script_check(),
    }
    ct, st, ec = record["comparison_table"], record["switching_difficulty_table"], record["experience_curve"]
    grid = record["effort_grid"]["at_frozen_value"]
    record["acceptance"] = {
        "vendored_resources_verified": not vendored_problems,
        "comparison_table_exact": ct["values_matched"] == ct["values_total"],
        "switching_table_exact_or_explained": st["rows_matched"] + st["rows_explained"] == st["rows_total"],
        "experience_curve_exact": ec["rows_matched"] == len(ec["rows"]),
        "effort_grid_one_unit_keys_within_0_1": all(g["max_abs_deviation_one_unit"] < 0.1 for g in grid.values()),
    }
    record["accepted"] = all(record["acceptance"].values())
    return record


def grids_for_export() -> dict:
    params = EffortParams(distance_scale=FROZEN_DISTANCE_SCALE)
    out = {}
    for name, factory in KEYBOARDS.items():
        keyboard = factory()
        variants = {"optimal": None}
        if name != "matrix":
            variants["traditional"] = traditional_fingers(keyboard)
        for variant, assignment in variants.items():
            grid = effort_grid(keyboard, params, assignment)
            out[f"{name}-{variant}"] = {
                "keyboard": keyboard.name, "fingers": variant, "distance_scale": FROZEN_DISTANCE_SCALE,
                "keys": [{"key": k.name, "x": k.x, "y": k.y, "width": k.width, "effort": round(grid[k.name].effort, 6),
                          "finger": grid[k.name].finger} for k in keyboard.keys],
            }
    return out


def write(record: dict, out_dir: Path = RESULTS) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []

    def dump(name: str, data) -> None:
        path = out_dir / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(data, str):
            path.write_text(data, encoding="utf-8", newline="\n")
        else:
            path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        written.append(path)

    slim = dict(record)
    slim["effort_grid"] = {k: v for k, v in record["effort_grid"].items() if k != "curve"}
    slim["model_grid_sensitivity"] = {k: v for k, v in record["model_grid_sensitivity"].items() if k != "generated_configs"}
    dump("reproduction.json", slim)
    dump("calibration-curve.json", record["effort_grid"]["curve"])
    for name, text in record["model_grid_sensitivity"]["generated_configs"].items():
        dump("model-configs/model_iso_" + name.replace("effort_", ""), text)
    params = EffortParams(distance_scale=FROZEN_DISTANCE_SCALE)
    ansi = ansi_staggered()
    dump("model-configs/model_ansi_traditional_config.dat",
         model_config_text(ansi, params, fingers="traditional", bottom="std"))
    for name, grid in grids_for_export().items():
        dump(f"effort-grids/{name}.json", grid)
    dump("kala-bangla-inventory.json", inventory())
    dump("REPORT.md", render_report(record))
    manifest = dict(record["manifest"])
    manifest["outputs"] = {p.relative_to(out_dir).as_posix(): sha256_file(p) for p in written if p.name != "run-manifest.json"}
    dump("run-manifest.json", manifest)
    return written


def render_report(r: dict) -> str:
    ct, st, ec = r["comparison_table"], r["switching_difficulty_table"], r["experience_curve"]
    eg, sens, quirk = r["effort_grid"], r["model_grid_sensitivity"], r["caseless_script_check"]
    m = r["manifest"]
    lines = [
        "# Phase 1 reproduction report",
        "",
        f"Generated {m['generated_utc']} by bangla-dh {m['bangla_dh_version']} (Python {m['python']}), "
        f"Kala commit `{m['kala_commit'][:12] or 'unknown'}`{'' if m['working_tree_clean'] else ' (uncommitted changes)'}.",
        f"Overall acceptance: **{'PASSED' if r['accepted'] else 'FAILED'}**.",
        "",
        "| Check | Result |",
        "| --- | --- |",
    ]
    for name, ok in r["acceptance"].items():
        lines.append(f"| {name.replace('_', ' ')} | {'pass' if ok else 'FAIL'} |")
    up = r["reference_integrity"]
    lines += ["", f"Upstream analyzer source: {'verified at the pinned commit' if up['upstream_source_ok'] else 'not verified — ' + '; '.join(up['upstream_problems'])}.", ""]

    lines += ["## 1. Layout comparison (compare.html)", "",
              f"{ct['values_matched']}/{ct['values_total']} published values reproduced exactly "
              f"({ct['rows_matched']}/{ct['rows_total']} rows).", "",
              "| Layout | Config | Base | SFB % | Bigram | Total | Match |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for row in ct["rows"]:
        rep = row["reproduced"]
        lines.append(f"| {row['label']} | {row['config']} | {rep[0]} | {rep[1]} | {rep[2]} | {rep[3]} | "
                     f"{'yes' if row['match'] else 'published ' + ' / '.join(row['published'])} |")

    lines += ["", "## 2. Switching difficulty (learn.html)", "",
              f"{st['rows_matched']}/{st['rows_total']} rows reproduced exactly; {st['rows_explained']} explained.", "",
              "| Layout | Keys moved (finger) | Keys moved | Σm | d | d without S2/S1 | Match |",
              "| --- | --- | --- | --- | --- | --- | --- |"]
    for row in st["rows"]:
        rep = row["reproduced"]
        status = "yes" if row["match"] else f"published d = {row['published'][3]}"
        lines.append(f"| {row['label']} | {rep[0]} | {rep[1]} | {rep[2]} | {row['switching_difficulty']:.2f} | "
                     f"{row['switching_difficulty_without_effort_ratio']:.2f} | {status} |")
    for row in st["rows"]:
        if "explanation" in row:
            lines.append(f"\n{row['label']}: {row['explanation']}")

    lines += ["", "## 3. Experience curve", "", f"p = log2(0.8) = {ec['p']:.10f}.", "",
              "| f (%) | Published C_f | Reproduced |", "| --- | --- | --- |"]
    lines += [f"| {row['f_percent']} | {row['published']} | {row['reproduced']} |" for row in ec["rows"]]
    ex = ec["specification_example"]
    lines += ["", f"Specification example (f = 5, m = 0.5, S2/S1 = 1.2): C_f = {ex['C_f_rounded_exponent']:.4f}, "
              f"D_i = {ex['D_i_rounded_exponent']:.4f} with the rounded exponent 0.678; "
              f"{ex['C_f_exact_exponent']:.4f} and {ex['D_i_exact_exponent']:.4f} with the exact exponent."]

    scan = eg["scan"]
    lo, hi = scan["widest_best_interval"]
    lines += ["", "## 4. Effort grid reconstruction (model.html)", "",
              "The grid generator is not published and P_d has no published value. With the published constants, "
              "the Euclidean nearest point of the inset activation area and a resting finger's own home key costing "
              f"P_f, scanning P_d over [{scan['range'][0]}, {scan['range'][1]}] gives at most "
              f"{scan['best_matches']}/{scan['scored_keys']} one-unit keys equal to the published value at one decimal, "
              f"for P_d in [{lo}, {hi}]. Frozen value: **P_d = {eg['frozen_distance_scale']}**.", "",
              "| Grid | 1u keys matched | All keys matched | Max abs deviation (1u) | Mismatches |",
              "| --- | --- | --- | --- | --- |"]
    for name, g in eg["at_frozen_value"].items():
        mism = ", ".join(f"{x['key']} {x['model']:.3f}≠{x['published']}" for x in g["mismatches"]) or "none"
        lines.append(f"| {name} | {g['one_unit_matches']}/{g['one_unit_keys']} | {g['all_matches']}/{g['keys']} | "
                     f"{g['max_abs_deviation_one_unit']:.3f} | {mism} |")
    lines += ["", "Modelling choices compared, each at its own best P_d:", ""]
    lines += [f"- {a['choice']}: {a['best_matches']}/{a['scored_keys']} one-unit keys" for a in eg["alternative_choices"]]
    for p in eg["published_config_vs_image"]:
        lines += ["", f"Published-source inconsistency: `{p['config']}` gives `{p['key']}` = {p['config_value']} "
                      f"(used by the comparison table) while the model.html grid shows {p['image_value']}."]

    lines += ["", "## 5. Sensitivity to grid rounding", "",
              "Ergonomic and traditional rows recomputed with unrounded model grids (P_d = "
              f"{sens['distance_scale']}) instead of the published one-decimal grids. "
              f"Ranking {'preserved' if sens['order_preserved'] else 'CHANGED'}.", "",
              "| Layout | Config | Published total | Model-grid total |", "| --- | --- | --- | --- |"]
    lines += [f"| {x['label']} | {x['config']} | {x['published_total']} | {x['model_grid_total']} |" for x in sens["rows"]]

    lines += ["", "## 6. Caseless scripts in the original analyzer", "", quirk["finding"], "",
              f"Probe layout `ক া ি` holds {quirk['key_chars']}; with every key effort 1.0 the base effort is "
              f"{quirk['base_effort_all_keys_effort_1']:.3f} instead of {quirk['expected_without_quirk']:.3f}.", ""]
    return "\n".join(lines)
