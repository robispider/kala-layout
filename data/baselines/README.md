# Baseline layouts

Reports compare the Bangla-DH layouts with existing **fixed** Bangla layouts
(`bangla_dh.scoring.baselines`). **Phonetic layouts (Avro Phonetic, Shohoj, any
layout type containing "phonetic") are never compared** (owner decision,
10 October 2026).

Every baseline is scored on every held-out corpus, on the model-optimal grid
(unrounded and one decimal) and on the traditional-fingering grid. The
comparison uses each baseline's **best** value of each metric over those
grids, so a Bangla-DH win does not depend on the fingering choice (D3).

## Where baselines come from

1. **`registry.json` → `baselines`** lists every baseline. UniJoy is Kala's
   `kala/layout/bn/UniJoy.json`, vendored at `data/kala/kala/layout/bn/UniJoy.json`.
   The five fixed layouts imported into Kala from Avro Keyboard (Windows Default,
   Probhat, Munir Optima (uni), Bornona, National (Jatiya)) are vendored in
   `data/baselines/layouts/<name>.json`, one `layout.json` each, and are typed with
   Kala's own formatting rules (`scoring/avro_fixed.py`, a port of Kala's
   `AvroFixedLayoutManager`). Every entry names its developer in `provenance`.
2. **Your own key-map file** for any other fixed layout (below).
3. **`discover`** (optional, absent by default): a folder in `registry.json` →
   `discover` is scanned for `*/layout.json` and every `avro-fixed` layout in it is
   added. The original research used Kala's imported-layouts folder; the registry
   now lists the vendored copies explicitly so results do not depend on one
   computer.

The files are third-party layout data kept only as benchmarks; see
`docs/DATASETS.md`.

## Adding a key-map file

1. Write `data/baselines/<name>.json`:

   ```json
   {
     "name": "Example",
     "provenance": "where the mapping comes from (URL, version, date checked)",
     "layers": {
       "base":  {"Q": "ঙ", "W": "য", "A": "ৃ", ";": "চ", "1": "১"},
       "shift": {"Q": "ং", "A": "ঋ"},
       "altgr": {"Q": "৺"}
     },
     "sequences": {"্া": "আ"}
   }
   ```

   * Keys are ANSI key names as in `results/phase1/effort-grids/ansi-optimal.json`:
     `Q`…`M`, `1`…`0`, `;` `,` `.` `/` `'` `[` `]` `-` `=` `` ` `` `\`.
   * Outputs are the exact text a key types; a key may type several characters.
   * `sequences` work as in Kala's files: typing the outputs on the left gives
     the text on the right (UniJoy's independent vowels).
   * Space is the thumb and is never listed.
2. Add an entry to `registry.json` → `baselines`:

   ```json
   {"name": "Example", "kind": "keymap", "file": "data/baselines/example.json",
    "fingering": "traditional", "provenance": "..."}
   ```

## Limits

* **AltGr has no v1 cost** (decision D2). Imported Avro layouts are typed with
  base and Shift only (their vowel formatting makes AltGr unnecessary for
  frequent text); a `keymap` file that needs AltGr gets J0 but no J1.
* **Text a layout cannot type is escaped** and costs nothing, so a large
  escaped share flatters a layout; the report shows it for every layout
  (for example `ৎ` or Bangla digits that exist only on AltGr).
* The metrics are the model's effort terms, not typing speed, learnability or
  error rate.
