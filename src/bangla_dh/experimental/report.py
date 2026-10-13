"""Reports never rank or select layouts by a conditional preference mean."""
from __future__ import annotations

import csv
import io


def csv_text(rows, columns):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=columns)
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def render(result):
    evidence = result["evidence"]
    lines = ["# Experimental evaluation season e1", "",
             "This is an additional diagnostic track. The published layouts, J0/J1, challenge and website are unchanged.", "",
             "## Evidence decision", "",
             "**Full-layout preference scoring and comfort-based candidate selection are withheld.**",
             "The source supplies 288 predicted pair values, covering same-hand pairs in two 12-key blocks. "
             "Shift/chords, cross-hand pairs and central keys lack support. Right-hand values use a symmetry assumption. "
             "No rule-generated values were added.", "",
             "| Evidence check | Result |", "| --- | --- |",
             "| Pinned source files and lookup benchmark | PASS |",
             "| Independent reproduction of held-out preference prediction | Not performed; no verified prediction artifact supplied |",
             "| Bangla human validation | Not performed |",
             "| Full-layout coverage / admission | FAIL; partial diagnostic only |", "",
             "The lookup benchmark verifies calculations, not predictive validity. "
             "Source per-pair uncertainties do not establish a layout confidence interval.", "",
             "Sources: [distributed pair table](" + evidence["source"]["files"][0]["source_url"] + "), "
             "[learning repository](" + evidence["source"]["learning_repository"] + "), "
             "[research paper](" + evidence["source"]["paper"] + ").", "",
             "## Stage 1: published layouts", "",
             "Canonical baseline encoding minimizes presses with frozen traditional-grid effort tie-breaking. "
             "The same encoded actions are scored under both fingering scenarios. Traditional-grid J0/J1 agree "
             "with recorded historical baseline scores; model-optimal baseline scores may differ from published "
             "scores because their encoding policy is held fixed here.", "",
             "J1 is modeled effort per counted unit including space. Pair support is the share of non-space "
             "action pairs matching source keys, base layers and traditional finger assignments. "
             "The conditional preference mean describes a different supported subset for each layout; "
             "**do not compare these means as complete comfort scores**.", ""]
    public = [r for r in result.get("scores", []) if r["public"]]
    for scenario in ("traditional", "model-optimal"):
        rows = [r for r in public if r["scenario"] == scenario]
        if not rows:
            continue
        lines += ["### " + scenario + " fingering", "",
                  "| Layout | Text | J1 | Source pair support | Conditional preference (partial) | Escaped units |",
                  "| --- | --- | --- | --- | --- | --- |"]
        for r in sorted(rows, key=lambda r: (r["corpus"], r["name"])):
            p = r["preference"]
            mean = "n/a" if p["conditional_pair_preference"] is None else f'{p["conditional_pair_preference"]:.6f}'
            support = "n/a" if p["supported_pair_share"] is None else f'{100*p["supported_pair_share"]:.1f}%'
            j1 = "n/a" if r["reference"]["J1"] is None else f'{r["reference"]["J1"]:.6f}'
            lines.append(f'| {r["name"]} | {r["corpus"]} | {j1} | {support} | {mean} | '
                         f'{100*r["diagnostics"]["escaped_unit_share"]:.2f}% |')
        lines.append("")
    candidates = result.get("candidates", [])
    lines += ["## Stage 2: retained candidates", "",
              f'{len(candidates)} distinct A/D maps were evaluated. '
              f'{result.get("stored_search_run_count", 0)} stored search outcomes were included; no new search ran.', "",
              "Every map is checked against the frozen inventory and 52-slot bijection, with fixed digits/punctuation retained. "
              "Training reference scores and descriptive frontier memberships are in candidates.json. "
              "The frontier uses existing J1, existing Shift effort M per text unit and same-finger/different-key count per text unit "
              "under model-optimal fingering. It is a diagnostic trade-off set, not a comfort recommendation. "
              "The preference diagnostic is excluded from rankings, frontiers and selection.", "",
              "No comfort shortlist or replacement layout was selected. The source evidence/coverage gate did not admit "
              "a complete preference evaluator. Candidate maps and corpus comparisons remain available for examination. "
              "These candidates were originally found under J1, so they are not a sample of the whole layout space.", "",
              "## Checks and reproducibility", ""]
    for name, check in result.get("checks", {}).items():
        lines.append(f'- {name}: {"PASS" if check else "FAIL"}')
    lines += ["", "The independent lookup benchmark, unit tests and original score agreement check software fidelity. "
              "None validates human comfort or speed. Published held-out texts are known benchmarks; "
              "they were not used to choose a new comfort winner.", "",
              "Derived numeric reports contain no corpus text. Input/output hashes, parameters, encoding policies "
              "and code revision are in run-manifest.json.", "",
              "## Next research requirement", "",
              "Obtain independently verifiable held-out preference predictions and data for central keys, "
              "cross-hand transitions and modifiers. Validate relevant conditions with Bangla typists before "
              "promoting this diagnostic to a whole-layout evaluator.", ""]
    return "\n".join(lines)
