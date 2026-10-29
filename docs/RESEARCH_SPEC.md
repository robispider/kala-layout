# Bangla-DH Pure — research and engineering specification

**Version 1.7 (10 October 2026).** Version 1.0 was the original plan; 1.1
updated it with what the Phase 1 code established; 1.2 records Phase 2; 1.3
records the owner's decisions on D1, D2 and D4 and the resulting v1 problem;
1.4 records Phase 3; 1.5 its news cross-check and the baseline registry;
1.6 records Phase 4 and the B/D repeated-press rule; 1.7 the mixed-corpus
search of A and D (changelog in section 15).

> **Note for this repository (12 October 2026).** This specification was written inside the Kala repository (`colemak-bangla/`). In `kala-layout` the Kala files it mentions are vendored under `data/kala/`, the texts come from the public `ban-dataset-collection` (`fetch-data`, `prepare-data`), the research store and BanLemma are not used, and the challenge kit lives in `challenge/`. Where this document and the code disagree, the code and `docs/REPRODUCE.md` are authoritative.

**How to read this document**

* Each section has a status: **[done]** (implemented and tested), **[next]**
  (the next work to do), **[planned]** (later phases) or **[open]** (a
  decision the project owner must make; see section 13).
* Where this specification and the code disagree, the code and its tests are
  authoritative for implemented phases. The exact Phase 1 mathematics is
  frozen in [colemak-model-spec.md](colemak-model-spec.md); this document
  summarizes it and does not restate every rule.
* New agent sessions start with [../AGENTS.md](../AGENTS.md).

---

## 1. Scientific objective

Develop **Bangla-DH Pure**, a keyboard layout for typing Bangla on a physical
keyboard, using the ergonomic model of Colemak Mod-DH as its foundation. The
system discovers candidate layouts automatically, evaluates them and selects
the best one under an explicitly defined mathematical objective.

Three goals:

1. Reproduce Colemak-DH's published calculations with its original
   methodology and source code. **[done]**
2. Extend that model to Bangla: vowel signs, hasant, conjuncts, several
   keyboard layers and Unicode composition. **[done: J0, and J1 with the v1
   Shift cost of D2]**
3. Establish verifiable optimality for a precisely defined optimization
   problem where computationally feasible, and report quantitative
   optimality gaps otherwise. **[planned]**

Colemak-DH does not claim a proof that it is the best possible layout. It
publishes a reproducible scoring model and comparisons with particular
layouts, and its author states that the ergonomic weights involve judgment.
Bangla-DH reproduces that model exactly and adds an optimization and
certification procedure for stronger, precisely scoped claims.

## 2. The original Colemak-DH methodology [done]

### 2.1 Sources

| Source | What it provides |
| --- | --- |
| [Typing Effort Grid](https://colemakmods.github.io/mod-dh/model.html) | Key-effort equations and finger geometry |
| [Layout Comparison](https://colemakmods.github.io/mod-dh/compare.html) | Bigram penalties, total effort, reference results |
| [Switching Difficulty](https://colemakmods.github.io/mod-dh/learn.html) | Learning-difficulty model |
| [keyboard-layout-analysis-tool](https://github.com/stevep99/keyboard-layout-analysis-tool) | Reference implementation (Kotlin), resources |

Pins (commit + SHA-256 of every file) are in `reference/sources.lock.json`.
The analyzer declares no license, so its source is fetched on demand into
`reference/upstream/` and never committed. Layouts, configs and frequency
tables are vendored from the CC0 `colemakmods/mod-dh` site.

### 2.2 How the original computes effort

The analyzer reads a **precomputed effort grid** from its config files,
rounded to one decimal. It does not evaluate the Fitts formula itself. The
formula belongs to a separate generator, described on model.html but not
published:

$$K(k,f) = P_f + \sqrt{(P_f F_y)^2 + (P_x F_x)^2}, \qquad F = \log_2(1 + P_d D)$$

| Constant | Value | Status |
| --- | --- | --- |
| $P_f$ index / middle / ring / pinky | 1.0 / 1.1 / 1.3 / 1.6 | published |
| $P_x$ lateral multiplier | 2.0 | published |
| Approach angle | 10° (staggered), 0° (split matrix) | published |
| Activation area | key footprint inset 0.3u on every side | published |
| Resting point offsets (x, y↑): index / middle / ring / pinky | (−0.04, −0.32) / (0.03, 0.16) / (0.00, 0.08) / (0.01, 0.09) | published |
| $P_d$ | **1.12** | not published; recovered by calibration (any value in [1.1195, 1.1220] is equivalent) |
| Contact point | Euclidean nearest point of the activation area | recovered |
| Own home key | costs exactly $P_f$ | recovered |

With these, 138 of the 142 one-unit keys in the three published grids match
the published value at one decimal, and all are within 0.073. These are model
parameters chosen by the Colemak-DH author, not universal physical constants.
Code: `src/bangla_dh/geometry/`.

### 2.3 Bigram penalties

Penalty by finger relationship and row difference (capped at 2):

| Pair | Same row | Adjacent rows | Top ↔ bottom |
| --- | --- | --- | --- |
| Same finger | 2.5 | 3.0 | 4.0 |
| Pinky–ring | 0.5 | 1.0 | 1.5 |
| Ring–middle | 0.1 | 0.2 | 0.3 |
| **Middle–index** | **−0.2** | **−0.1** | **0.0** |

Version 1.0 said other combinations carry no penalty. In fact the
ergonomic, traditional and matrix configs that produce the published numbers
give middle–index pairs a *benefit* (negative penalty). The compare.html
table does not show it. For Colemak-DH ergonomic it contributes −0.017 of the
0.065 bigram score. Further rules:

* Same-finger pairs need two *different* characters (`ee` is free).
* Neighbour pairs are fingers with adjacent numbers. The penalty is booked
  to the outer finger, and right-hand fingers mirror the left-hand table.
* Shift costs nothing: `:` costs exactly what `;` costs.
* Space is not in the model. Frequencies are re-normalized over the
  characters on the layout, and bigrams across a space are never counted.

$$E = E_{\text{base}} + E_{\text{bigram}}$$

Published Colemak-DH on the ergonomic (ISO angle-mod) configuration: base
1.670, bigram 0.065, total 1.735. **Reproduced exactly**, together with all
60 values of the 15-layout comparison table.

### 2.4 Switching difficulty

Movement score $m$: unchanged 0, same finger 0.25, other finger on the same
hand 0.5, mirrored finger on the other hand 0.75, other finger on the other
hand 1.0, plus per-key overrides (Colemak-DH angle mod: Z X C 0.25, V 0).

$$p = \log_2 0.8 = -0.3219280949\ldots,\qquad C(f) = \frac{f^{1+p}}{1+p},\qquad D = \sum_i m_i\, C(100 u_i)\,\frac{S_{2,i}}{S_{1,i}}$$

The implementation includes the $S_2/S_1$ ratio and measures frequency in
percent. learn.html's second formula, without the ratio, is the pre-2021
model. One published cell (Qwpr, d = 18) still uses it: the current model
gives 14.41 and the old one 17.58. All other rows reproduce.

Worked example (f = 5, m = 0.5, $S_2/S_1$ = 1.2): $C_f = 5^{0.678}/0.678 \approx 4.3921$
and $D_i \approx 2.6353$. Learning difficulty is reported separately and is
**not** part of Bangla-DH Pure's objective.

## 3. Pipeline

| # | Stage | Status | Code / output |
| --- | --- | --- | --- |
| 01 | Original Colemak-DH replication | done | `bangla_dh.colemak`, `bangla_dh.geometry`, `results/phase1/` |
| 02 | Bangla corpus preparation | done (Wikipedia + BanLemma, D4 default) | `bangla_dh.corpus`, `data/corpus-v1.json`, `results/phase2/` |
| 03 | Unicode and typing grammar | done | `bangla_dh.bangla`, `data/bangla-symbols-v1.json` |
| 04 | Keyboard geometry model | done (ANSI grid generated) | `bangla_dh.geometry`, `results/phase1/effort-grids/` |
| 05 | Frequency and transition matrices | done | `bangla_dh.corpus.frequency`, `results/phase2/frequencies/` |
| 06 | Global candidate search | done (best found, Phase 3) | `bangla_dh.search`, `bangla_dh.bangla.styles`, `data/problem-v1.json`, `results/phase3/` |
| 07 | Exact verification | done (bounded near-optimum, scoped proofs; Phase 4) | `bangla_dh.search.integer`, `search.bounds`, `search.lp_bound`, `search.cpsat`, `phase4.py`, `results/phase4/` |
| 08 | Independent evaluation | sensitivity done (Phase 4); typists planned | `bangla_dh.scoring.sensitivity`, `results/phase4/sensitivity.json` |
| 09 | Keyboard generation | planned | planned `bangla_dh.export` |

Every stage writes only inside `colemak-bangla/`; Kala's data is read in place
and never modified (`bangla_dh.paths.output_path` enforces this).

Every stage saves its inputs, outputs, configuration and validation results
with SHA-256 hashes (see `results/phase1/run-manifest.json` for the format).
A stage never silently changes the corpus or the scoring constants.

## 4. Problem definition (v1)

Owner decisions of 10 October 2026 (section 13) define v1:

| Parameter | Bangla-DH Pure v1 | Notes |
| --- | --- | --- |
| Physical keyboard | ANSI row-staggered | The 30 main keys and the number row sit exactly where they do on ISO, so the reconstructed grid applies unchanged. |
| Character layers | **Base and Shift** | Bangla has no letter case, so Shift is a second set of symbols. A third (AltGr) layer for conjuncts is a later, optional add-on for power users. |
| Searched keys | the 26 letter keys (Q–P, A–L, Z–M) | `, . ; /` keep their US punctuation. |
| Candidate slots | **52** (26 keys × 2 layers) | |
| Fixed, not searched | Bangla digits on the number row and numeric keypad (base layer); ASCII punctuation `, . ; : ' " ( ) - ! ?` at US positions | `.` is therefore typable. |
| Searched symbols | **52**: 35 consonants (ড় ঢ় য় included), ্, ং ঃ ঁ ৎ, ।, plus the vowel set of the style (below) | Exactly fills the slots. |
| Vowel-entry styles | evaluated separately, each its own search (section 7.1) | |
| Not on v1 keys | ZWNJ, ZWJ (no key); ঽ ॥ — (third layer later) | Together < 0.01 % of text. |
| Finger assignment | model-optimal ANSI grid | `effort-grids/ansi-optimal.json`; equivalent to the angle mod (D3 default) |
| Primary objective | $J_1$ with the model Shift cost (section 6.6); $J_0$ reported alongside | |
| Learning-difficulty penalty | zero | |
| Output | standard Unicode Bangla, NFC | |
| Conjuncts | consonant + hasant + consonant | Counted per keystroke; conjunct statistics are kept for the future third layer |
| Corpus | Bangla Wikipedia only (train / held-out by document) | D4 |
| Search | multi-start heuristics + exact solver | |
| Verification | independent scorer + bounds | |

Typing units are counted per keystroke, never per conjunct: ক্ত is ক, ্, ত.
Every searched symbol sits on exactly one slot; independent vowels or vowel
signs not on a slot are produced by the style's rule, so every supported
character still has one documented way to be typed.

### 4.1 Bangla Unicode correctness

The optimizer works on Unicode code-point units, not drawn glyphs:

| Visual | Code points |
| --- | --- |
| কি | U+0995 U+09BF |
| ক্ত | U+0995 U+09CD U+09A4 |
| ক্ষ | U+0995 U+09CD U+09B7 |
| ক্র | U+0995 U+09CD U+09B0 |

The keyboard must satisfy, for every supported text $T$:

$$\operatorname{NFC}(\operatorname{Decode}(\operatorname{Encode}_L(T))) = \operatorname{NFC}(T)$$

Facts established while preparing Phase 2:

* ড় ঢ় য় (U+09DC, U+09DD, U+09DF) are **composition exclusions**. NFC turns
  them into ড/ঢ/য + nukta (U+09BC). Kala's `Alphabet.json` stores the
  precomposed forms. The typing grammar must define one canonical form
  (recommended: a single key emitting the NFC two-code-point sequence) and
  normalize the corpus the same way.
* Kala's `Alphabet.json` conjunct list contains at least one non-Bengali
  entry (`ধ` + Devanagari virama U+094D + Devanagari ष U+0937) and several
  entries that are not consonant clusters (for example `য়ার`, `রল`). Phase 2
  must validate the inventory against Unicode properties rather than trust it.
* Some Wikipedia words contain hasant directly followed by a vowel sign
  (legacy-conversion artifacts, e.g. `র্ী`). In UniJoy, typing ্ then a vowel
  sign produces the independent vowel, so such text is not typable there; the
  encoder escapes it rather than producing a different word.
* The original analyzer treats Bangla letters as caseless letters that
  "shift" to themselves, so every key holds its character twice and base
  effort is counted twice. Bangla scoring therefore uses a new
  Bangla-aware scorer (section 6); the port remains the English regression
  reference.

## 5. Bangla corpus [done, D4 default]

Phase 2 built `bangla-corpus-v1` (config `data/corpus-v1.json`, report
`results/phase2/REPORT.md`): the atomic Wikipedia dump streamed in place from
Kala's research store (hash-checked), wikitext cleaned to prose
(`bnwiki-prose-v1`), normalized (`bangla-dh-text-v1`), deduplicated by
paragraph and split 90/10 by document: 171,685 train and 19,063 held-out
articles, 445 M characters, 390 M training units. BanLemma's 1,254 sentences
are a second, held-out domain. Optimization frequencies use Wikipedia train
only (α = 1) until D4 is decided.

### 5.1 Sources

Available in the Kala repository (hashes in
`results/phase1/kala-bangla-inventory.json`; `bangla-dh inventory-kala`):

| Source | Content | Access |
| --- | --- | --- |
| `bnwiki-atomic-v1/source/bnwiki-atomic.xml.gz` | Atomic-normalized Bangla Wikipedia dump | 18-part object; restore with `scripts/project_data.py restore` (3.7 GB) |
| `bnwiki-atomic-v1/gold_word_frequency.tsv` | `word  count  gold` | Readable in place from `project-data/research/objects` |
| `bnwiki-atomic-v1/gold_word_bigram.tsv` | Word-bigram counts | gzip object |
| `bnwiki-atomic-v1/dispersion-v1/dispersion.tsv` | Per-word document dispersion | in place |
| `banlemma-atomic-v1/.../gt-test-data.tsv` | BanLemma sentences (not Wikipedia) | in place |
| `tools/kala-eval/datasets/top20k.tsv` | Top 20k words with counts | tracked file |

All of this is **encyclopedic** text (Wikipedia). The planned domain mixture
needs further, appropriately licensed sources ([open] D4). The AI4Bharat
IndicNLP corpus (about 836 M Bengali tokens, mostly news) is a candidate.

Proposed domain weights, to be validated rather than assumed:

| Domain | Weight |
| --- | --- |
| News and journalism | 25 % |
| Books and literature | 25 % |
| Government and administration | 20 % |
| Everyday conversational Bangla | 20 % |
| Encyclopedic and educational | 10 % |

### 5.2 Frequencies

For domain $d$ with $N_d$ accepted typing units, unit counts $n_{i,d}$,
bigram counts $n_{ij,d}$ and fixed weights $\alpha_d$ ($\sum_d \alpha_d = 1$):

$$u_i = \sum_d \alpha_d \frac{n_{i,d}}{N_d}, \qquad v_{ij} = \sum_d \alpha_d \frac{n_{ij,d}}{N_d}$$

Rules:

* Compute from running text, not from word-frequency tables. Word tables
  lose the transitions across spaces and punctuation.
* Represent space explicitly as a typing unit, unlike the original model.
  How it enters the objective is [open] D2.
* Never count transitions across document boundaries.
* Split train and held-out data **by document**.
* Record Unicode normalization (NFC), deduplication, Bangla-language
  filtering, joiner (ZWJ/ZWNJ) and punctuation handling, and out-of-inventory
  handling, each with a version.
* Use binary64 for Bangla frequencies. The binary32 storage is a property of
  the original tool and is kept only in the English regression port.

## 6. Objective

### 6.1 Assignment

Symbols $\mathcal C = \{c_1..c_n\}$ and physical key-layer actions
$\mathcal A = \{a_1..a_m\}$. A layout is an injective map $L:\mathcal C\to\mathcal A$.

### 6.2 Key effort [done]

$K(a)$ is the reconstructed model effort of the action's physical key with
its assigned finger: P_d = 1.12, unrounded (`effort-grids/ansi-optimal.json`).
Unrounded grids move the published English totals by only +0.001 to +0.007
and keep their ranking (Phase 1 report, section 5). Every result is also
reported on the one-decimal grid, so that both remain comparable to the
published numbers.

### 6.3 Unigram effort

$$E_1(L) = \sum_i u_i\, K(L(c_i))$$

### 6.4 Bigram effort

$$E_2(L) = \sum_{i \ne j} v_{ij}\, B(L(c_i), L(c_j))$$

$B$ is the table of section 2.3, **including the middle–index benefit**, with
the row difference capped at 2 and pairs of the same symbol excluded.

### 6.5 Primary objective (Colemak fidelity)

$$\min_{L \in \mathcal F} J_0(L) = \sum_i u_i K(L(c_i)) + \sum_{i\ne j} v_{ij} B(L(c_i), L(c_j))$$

$\mathcal F$ is the set of legal assignments. There are no bonuses for
preferred letter groups or for similarity to English Colemak. $J_0$ is
solved and certified first.

### 6.6 Bangla extensions

$M(a)$ is the modifier effort of an action (Shift, AltGr held) and
$Q(a,b)$ an extra transition penalty for layer changes not covered by $B$:

$$J_1(L) = J_0(L) + \lambda_m \sum_i u_i M(L(c_i)) + \lambda_t \sum_{i,j} v_{ij} Q(L(c_i), L(c_j))$$

Phase 2 finding: with $M = 0$ the three layers are equally cheap, so the
minimum of $E_1$ alone stacks three symbols on each of the cheapest keys
(`results/phase2/REPORT.md`, section 7). A 90-slot search under $J_0$ is
therefore only meaningful once D2 fixes a layer cost or restricts the layers.

**v1 Shift cost (owner decision D2, 10 October 2026).** A Shift-layer
action costs one extra keystroke on the Shift key of the *other* hand, with
that key's effort from the same reconstructed grid:

$$M(a) = \begin{cases} 0 & a \text{ on the base layer} \\ K(\text{RShift}) = 4.610 & a \text{ shifted, key on the left hand} \\ K(\text{LShift}) = 3.308 & a \text{ shifted, key on the right hand} \end{cases}$$

with $\lambda_m = 1$ and $Q = 0$. No new constant is introduced, but two
modelling assumptions are: Shift is pressed for every shifted symbol (not held
across consecutive shifted symbols), and the Shift press adds no bigram
penalty. A later typing-time measurement replaces or checks $M$ (sensitivity
analysis, section 9). $J_0$ is always reported next to $J_1$.

$\lambda_m, \lambda_t$ are new research parameters, not Colemak-DH constants.
They are estimated or validated from measured keypress timings and comfort
experiments, never assigned arbitrarily. $J_0$ and $J_1$ are always reported
separately. In the original model Shift is free, so any $M$ is a pure
extension.

## 7. Search [done: Phase 3, best found]

### 7.1 Vowel-entry styles

v1 has room for one vowel set, not two. Each style is a separate search
problem; the reports compare their best layouts.

| Style | On keys | Other vowel form | Extra keystrokes |
| --- | --- | --- | --- |
| A, UniJoy-style | 10 vowel signs + অ | independent vowel = ্ then the vowel sign | 1 per independent vowel except অ (4.6 % of non-space units are independent vowels) |
| B, sign key, double tap | 10 vowel signs + অ | independent vowel = the sign key tapped twice | 1 per independent vowel except অ |
| C, vowel key, double tap | 11 independent vowels | vowel sign = the vowel key tapped twice | 1 per vowel sign (26.7 % of non-space units) |
| D, context | 10 vowel signs + অ | one tap; the context picks the form | 1 only for an independent vowel right after a consonant (বই, দই, বউ) |

Style D, exact rule. A vowel key holds one vowel (its sign and its
independent form; অ has only the independent form):

* After a consonant unit (ক…হ, ড় ঢ় য়), one tap gives the **vowel sign**.
* Anywhere else (start of a word, after space, punctuation, an independent
  vowel, a vowel sign, ং ঃ ঁ ৎ or ্), one tap gives the **independent
  vowel**.
* Override: tapping the same vowel key again right after it produced a sign
  turns that sign into the independent vowel (ব, ি, ি → বই). This is the only
  case with an extra keystroke.

Open points to settle while implementing D, not owner decisions unless they
change the rule above: whether a vowel after ্ should give the sign (it is
invalid text either way and is escaped), and how D interacts with the future
third (conjunct) layer. **Settled in Phase 3:** after ্ a vowel key gives the
independent vowel (rule unchanged), so hasant + vowel sign is escaped as in
A; the third layer is not part of v1.

**Collisions found in Phase 3.** The double-tap rules could not type every
valid text: B and D could not type a vowel sign followed by the same vowel's
independent form (তিনিই, এটিই, সিইও; about 0.01 % of units), C cannot type the
same independent vowel twice (এএফসি).

**Repeated presses in B and D (owner rule, 10 October 2026).** Timing-free:
consecutive presses of one vowel key whose first press gave a sign (always
in B; after a consonant in D) form a run. The run is split into pairs, with
one single press at the start when its length is odd; a single is the sign,
a pair the independent vowel:

| Presses | Output |
| --- | --- |
| 2 | ই |
| 3 | ি ই (তিনিই) |
| 4 | ই ই |
| 5 | ি ই ই |

The next different key (or an escape, or space) ends the run; no timer is
needed. The decoder rewrites the run's output on every press, so the screen
always shows the buffered result. In D a run that starts outside a consonant
context does not pair (each press gives one more independent vowel). Cost:
D needs 4 presses for নইই (3 before). Implemented in `bangla.styles` and,
separately, in `scoring.verify`; Phase 3 and its cross-check were
regenerated with it (no label of any best layout moved; B and D J1 +0.0003).
**C is unchanged:** its double press gives the sign, so a three-press rule
for আআ would need its own definition (owner point). The remaining escapes are
invalid text (hasant + sign, a doubled sign, an independent vowel followed by
its own sign) and C's আআ.

**Phase 3 implementation.** `bangla.styles` models every style as a typing
machine that sees only key labels (`Style.press`); the encoder chooses, unit
by unit, the fewest keystrokes whose simulated output equals the text, and
escapes units no rule can type. Labels do not depend on the layout, so each
style has its own keystroke tables (`search.keystrokes`, from the Phase 2
token tables, same N as Phase 2). The search (`search.anneal`) treats a style
as a QAP with a linear term (52 labels, 52 slots, fixed keys folded in),
keeps $G_{is}$, the cost of label $i$ on slot $s$ given the others, for O(1)
swap deltas, and runs per seed: simulated annealing (1 M pair swaps,
geometric cooling over three decades from a calibrated $T_0$), steepest
descent, and 1,000 iterations of iterated local search; 64 seeds per style,
then a confirmation search from each best layout.

A repeated key costs its effort twice and no bigram penalty (repeats are free
in the original model). Each style's typing rule is a key-map sequence
(`bangla.grammar.KeyMap`), and the NFC round trip must hold for it. Because no
style uses composite keys, the stream of typed symbols is the same for every
layout of a style, so each style gets its own unit and pair frequencies and
the search can use fast delta scoring. Style D is context-sensitive, but
its typed-symbol stream is still a function of the text alone (the context is
the previous unit, not the layout), so the same holds; its decoder needs
context, which `KeyMap` does not support yet (Phase 3, task 2).


$30! \approx 2.65 \times 10^{32}$ arrangements for the base layer alone, so
exhaustive search is impossible. Plan: simulated annealing plus iterated
local search, followed by exact methods (section 8).

```
optimize(seed, steps, corpus, model):
    rng = Random(seed); current = feasible_layout(rng)
    best = current; current_score = best_score = score(current)
    for t in 0..steps-1:
        candidate = mutate(current, rng)          # swaps, short cycles, cross-layer exchanges
        delta = score(candidate) - current_score
        if delta <= 0 or rng.random() < exp(-delta / temperature(t)):
            current, current_score = candidate, current_score + delta
        if current_score < best_score: best, best_score = copy(current), current_score
    return best, best_score
```

* Use incremental (delta) scoring for swaps; a full re-score per move is too
  slow.
* Start from frequency-sorted and random feasible layouts. Record each run's
  seed, schedule and best score.
* The original tool has its own annealer (`sa/SimulatedAnnealing.kt`). It
  can serve as an English sanity baseline, not as the Bangla optimizer.

Deterministic search is reproducible but proves nothing about global
optimality.

## 8. Optimality [done: Phase 4, bounded near-optimum]

### 8.1 Quadratic assignment

$x_{ia} \in \{0,1\}$; $\sum_a x_{ia} = 1\ \forall i$; $\sum_i x_{ia} \le 1\ \forall a$;
forbidden pairs fixed to 0.

$$E_1 = \sum_{i,a} u_i K_a x_{ia}, \qquad E_2 = \sum_{i,j,a,b} v_{ij} B_{ab}\, x_{ia} x_{jb}$$

### 8.2 Linearization

$z_{ijab} = x_{ia}x_{jb}$ with $z \le x_{ia}$, $z \le x_{jb}$, $z \ge x_{ia} + x_{jb} - 1$.
The full expansion has millions of variables. Use sparse transitions (only
pairs with $v_{ij} > 0$ and $B_{ab} \ne 0$), stronger bounds and growing
exact sub-problems.

### 8.3 Bounds

$LB \le J^* \le UB = J(L_{\text{best}})$. If $LB = UB$, the layout is optimal
under the stated model. Otherwise report

$$\text{Gap} = 100\,\frac{UB - LB}{\max(1, |UB|)}\ \%$$

and call the result *best known*, not optimal.

**Correction to v1.0:** because middle–index penalties are negative, the
unigram-only assignment is **not** a valid lower bound. A valid elementary
bound is

$$LB_0 = \min_L E_1(L) + \sum_{i \ne j} v_{ij} \min_{a \ne b} B_{ab}$$

(minimum over all pairs of distinct actions; with this table $\min B = -0.2$). Stronger bounds come from solver relaxations
(Gilmore–Lawler-type bounds for the QAP, CP-SAT best bound).

### 8.4 Integer arithmetic

Pre-compute $\widehat K_a = \operatorname{round}(10^6 K_a)$, and scale
frequencies and penalties to integers with a frozen rule. Freeze the scale,
the transcendental implementation (Python `math`), the rounding rule and
coefficient hashes ([open] D5). A claim about the unrounded model needs
rigorous rounding-error bounds.

### 8.5 Solver

Google OR-Tools CP-SAT: integer models, objective bounds, and a clear
difference between `OPTIMAL` and stopping within a gap tolerance. Disable
gap-based early stopping when an exact optimum is required. Check every
returned solution and bound with the independent scorer. Re-running the same
solver is replication, not independent proof. When proof is infeasible,
report UB, LB, runtime and scope.

Scope labels must be exact: proving the frozen 30-symbol core optimal while
the other mappings are held fixed is **not** proof for the unrestricted
90-slot keyboard.

## 9. Independent verification [mathematical and parameter sensitivity done (Phase 4); typists planned]

* **Mathematical:** legal and complete assignment, normalized text output,
  objective recomputed by a scorer that shares no code with the search
  ($J_{\text{verify}}(L)$ must equal the optimizer's integer objective).
* **Corpus generalization:** held-out news, government, literature and
  conversational text.
* **Parameter sensitivity:** vary $P_x$ around 2.0, $P_d$ over at least the
  calibrated interval, and the finger factors:

$$R(L) = \Pr_{\theta \sim \Theta}\left(J_\theta(L) \le J_\theta(L_{\text{baseline}})\right)$$

  This is a model-sensitivity statistic, not a probability of comfort.
* **Typists:** speed, error rate, learning curve and comfort over repeated
  sessions.

## 10. Software architecture

Implemented (Python ≥ 3.10, standard library only):

```
colemak-bangla/
├── AGENTS.md                     start here (agents and new contributors)
├── docs/RESEARCH_SPEC.md         this document
├── docs/colemak-model-spec.md    frozen Phase 1 mathematics
├── src/bangla_dh/
│   ├── colemak/                  port of the original analyzer (English regression)
│   │   ├── javacompat.py         binary32, Java formatting, Java character rules
│   │   ├── keyboard.py           layouts, keys, configs
│   │   ├── frequency.py          frequency tables, FreqAnalysis
│   │   ├── analysis.py           effort analysis and reports
│   │   └── switching.py          switching difficulty, experience curve
│   ├── geometry/
│   │   ├── keyboards.py          ISO, ANSI, split-matrix geometry
│   │   ├── effort_model.py       reconstructed effort grid
│   │   ├── calibrate.py          P_d recovery against published grids
│   │   └── analyzer_config.py    analyzer configs from the model
│   ├── reference.py              pins and upstream fetch
│   ├── kala_data.py              Kala Bangla data inventory
│   ├── reproduce.py              Phase 1 run and report
│   └── cli.py
├── reference/                    lock file, vendored resources, published targets
├── results/phase1/               committed Phase 1 baseline
└── tests/
```

Phase 2 added `paths.py` (write guard), `bangla/` (inventory, normalization,
typing grammar, key maps, encode/decode, NFC round trip), `corpus/`
(read-only research-store reader, wikitext cleaner, corpus build and split,
token and unit frequency tables), `scoring/` (key model, $J_0$ scorer,
independent verifier, UniJoy and English key maps), `phase2.py` and
`phase2_report.py`, with frozen inputs in `data/`.

Phase 3 added `bangla/styles.py` (vowel-entry styles A–D), `search/`
(`problem.py`: the v1 problem file; `keystrokes.py`: per-style keystroke
tables; `anneal.py`: delta-scored annealing and iterated local search), J1
in `scoring/` (`KeyModel.modifier_effort`, both scoring routes and
`verify.verify_style`), `phase3.py` and `phase3_report.py`.

Phase 4 added `search/integer.py` (exact integer coefficients),
`search/bounds.py` (LB0, Gilmore–Lawler, Hungarian, exhaustive exchange and
sub-problem enumeration), `search/lp_bound.py` (cell-level RLT LP with an
exact weak-duality certificate), `search/cpsat.py` (CP-SAT models: full
problem, free-label sub-problems, radius), `scoring/sensitivity.py` (θ grids
and action tables), `phase4.py` and `phase4_report.py`. OR-Tools
(`ortools==9.14.6206`, optional extra `phase4`) is the project's only
dependency, approved by the owner on 10 October 2026; every other module is
standard library.

Planned modules: `export/` (Keyman, layout files, typing tests). Generated data goes under `results/<phase>/` with a run
manifest. Large corpora stay outside Git.

## 11. Commands

| Command | Status |
| --- | --- |
| `bangla-dh reproduce-colemak` | done |
| `bangla-dh analyze`, `switching`, `freq-analysis` | done (original model) |
| `bangla-dh effort-grid --keyboard ansi` | done |
| `bangla-dh calibrate-grid`, `verify-reference`, `fetch-upstream`, `inventory-kala` | done |
| `bangla-dh build-inventory` | done |
| `bangla-dh build-corpus` (config `data/corpus-v1.json`) | done |
| `bangla-dh compute-frequency` | done |
| `bangla-dh evaluate-phase2` (checks, baselines, report) | done |
| `bangla-dh build-problem`, `style-frequency` | done |
| `bangla-dh optimize [--styles A B C D] [--seeds N]` (objective J1) | done |
| `bangla-dh evaluate-phase3` (checks, J1 baselines, held-out comparison, report) | done |
| `bangla-dh certify [--styles ...] [--skip ...]`, `certify-lp`, `sensitivity`, `evaluate-phase4` | done (Phase 4; needs OR-Tools) |
| `bangla-dh benchmark --dataset heldout` | planned (held-out Wikipedia is part of `evaluate-phase3`) |
| `bangla-dh export --format keyman` | planned |
| `bangla-dh report` | planned |

Every run writes a machine-readable manifest: source revisions, SHA-256 of
inputs and outputs, normalization version, model parameters, seeds and
solver settings. Keyman is the export target because its rules support
context-sensitive Unicode output.

## 12. Deliverables

| Deliverable | Acceptance | Status |
| --- | --- | --- |
| Colemak reproduction report | Published results matched at their precision | **done**: `results/phase1/REPORT.md` |
| Frozen model specification | Every rule tested | **done**: `docs/colemak-model-spec.md` |
| Geometry model | Every key's score reproducible | **done**: P_d = 1.12, ANSI/ISO/matrix grids |
| Corpus specification | Sources, preprocessing, splits, weights, checksums | **done** (D4 default): `data/corpus-v1.json`, `results/phase2/corpus-manifest.json` |
| Unicode input specification | Every symbol and sequence unambiguous; NFC round trip | **done**: `data/bangla-symbols-v1.json`, `bangla_dh.bangla.grammar`; 0 round-trip failures on 454,000 texts |
| Cost model | Equations, constants, normalization | **done**: $J_0$ and $J_1$ (D2) in the table scorer, the token scorer and the independent verifier |
| Optimizer | Reproducible with fixed seeds | **done**: `bangla-dh optimize`, 64 seeds per style, `results/phase3/search/` |
| Optimality report | Proven scope and bounds, or explicit gap | **done**: `results/phase4/REPORT.md` (bounded near-optimum per style, scoped proofs) |
| Sensitivity analysis | Results across parameter ranges | **done** (model parameters): `results/phase4/sensitivity.json`; typing-time measurement planned |
| Keyboard implementation | Correct Unicode output | **done for Kala**: `results/kala-keyboards/` (Kala Goti = A, Kala Jhor = D); Keyman planned |
| Typing evaluation | Held-out and human comparison | planned |

## 13. Phases, decisions and next tasks

| Phase | Content | Status |
| --- | --- | --- |
| 1 | Reproduce the original model; pin sources; regression tests | **done** (10 Oct 2026) |
| 2 | Bangla dataset, Unicode rules, frequencies, Bangla scorer, baselines | **done** (10 Oct 2026) |
| 3 | Seeded candidate search, held-out comparison | **done** (10 Oct 2026) |
| 4 | Integer models, certified bounds, scope labels, sensitivity | **done** (10 Oct 2026) |
| 5 | Installable keyboard, user testing, replication | **next** |

### Open decisions (project owner)

| ID | Decision | Default if not decided |
| --- | --- | --- |
| D1 | Exact v1 symbol inventory and which symbols may sit on Shift/AltGr | **Decided 10 Oct 2026:** digits on the number row and keypad; no keys for ZWNJ/ZWJ; ্ has its own key; ASCII punctuation fixed at US positions; two layers (base, Shift), third conjunct layer later; vowel entry compared across styles A–D (sections 4, 7.1) |
| D2 | Space, punctuation and layer costs ($M$, $Q$, $\lambda$) | **Decided 10 Oct 2026:** Shift = the other hand's Shift key from the model grid, $\lambda_m = 1$, $Q = 0$ (section 6.6); space on the thumb at no cost; to be checked by measurement later |
| D3 | Finger assignment on ANSI: model-optimal (angle-mod-like) or traditional | Model-optimal |
| D4 | Corpus sources beyond Wikipedia and their licenses; domain weights | **Decided 10 Oct 2026:** Bangla Wikipedia only for Phases 3–4 (BanLemma is not used from Phase 3 on). **Updated 10 Oct 2026:** the A and D layouts for typing tests are searched on 0.5 × bnwiki/train + 0.5 × newspaper/train (`results/mix-search/`) |
| D5 | Integer scale for certification | $10^6$ (used in Phase 4; exact for the six-decimal grid) |
| D6 | Keep the middle–index benefit | Yes (Colemak fidelity) |

### Phase 3 outcome

All five tasks are done; `results/phase3/REPORT.md` has the numbers. Best
found layouts under $J_1$ (held-out Wikipedia, model-optimal grid):

| Style | Keystrokes per non-space unit | $J_1$ | $J_0$ |
| --- | --- | --- | --- |
| D, context | 1.002 | 1.834 | 1.543 |
| A, UniJoy-style | 1.039 | 1.867 | 1.573 |
| B, sign double tap | 1.038 | 1.880 | 1.588 |
| C, vowel double tap | 1.267 | 2.153 | 1.840 |
| UniJoy (Kala) | 1.002 | 2.808 | 2.174 |

Each best layout was reached by 4–19 of 64 independent seeds and was not
improved by 30,000 further local-search iterations; the train and held-out
scores agree within 0.001; the independent verifier matches the table scorer
within 2e-10 and N, keystroke and escape counts exactly; NFC round trips
have 0 failures on 227,000 texts per style. The elementary bound $LB_0$
leaves gaps of 10–11 %, so these are **best found**, not bounded or proven.
Most of the gain over UniJoy is fewer same-finger pairs (E2 0.035 against
0.402) and fewer Shift presses (M 0.29 against 0.63).

### Phase 4 outcome

All four tasks are done; `results/phase4/REPORT.md` has the numbers. Scope
of every certificate: the v1 problem of the style (52 searched labels on the
52 v1 slots, fixed keys as in `data/problem-v1.json`), J1, model-optimal
grid, middle–index benefit kept, bnwiki/train keystroke counts, integer scale
$10^6$.

| Style | Best found J1 (UB) | Certified LB (cell LP) | Gap | Proven optimal within |
| --- | --- | --- | --- | --- |
| D | 1.8346 | 1.7578 | 4.19 % | any move of ≤ 5 labels; top-20 labels free; Shift layer free |
| A | 1.8674 | 1.7869 | 4.31 % | same |
| B | 1.8807 | 1.8034 | 4.11 % | same |
| C | 2.1531 | 2.0668 | 4.01 % | same |

* Every layout is a **bounded near-optimum** (section 14): no layout of the
  scope is better by more than the gap. No style is proven optimal: the
  base layer (26 labels) and the top-24 sub-problem stay open after 600 s of
  CP-SAT.
* Proven between styles: C's lower bound exceeds the best found J1 of A, B
  and D, so no C layout of the scope beats them. The order D < A < B is
  best found only (the gaps exceed the differences).
* Bounds: LB0 10–11 %, Gilmore–Lawler 6.0–6.2 %, CP-SAT on the full problem
  (15 min) 4.8–5.5 %, cell LP 4.0–4.3 %. The cell LP (481,390 columns) is
  solved by PDLP (GLOP did not finish in 30 min) and certified by weak
  duality in exact integer arithmetic from the stored duals.
* The integer model is exact (the grid has six decimals, B is a multiple of
  0.1); the independent verifier, now summing exactly, reproduces it on the
  training text as an exact rational.
* Sensitivity (1,000 θ): D has the lowest J1 of the four styles for every θ;
  A, B and D beat every baseline for every θ (C loses to Windows Default for
  63 % of θ). Re-optimizing for one extreme parameter gains ≤ 0.5 %, except a
  cheaper middle finger (P_f 0.935): about 1 %.

### Phase 4 task list (done)

1. **Integer coefficients** (D5 default $10^6$): done, exact (`search/integer.py`).
2. **Bounds:** done: LB0, Gilmore–Lawler (stdlib, re-checked by OR-Tools),
   cell-level RLT LP (certified from duals), CP-SAT full problem.
3. **Certificates:** done: UB, LB, gap and scope per style; exhaustive
   exchange certificate (≤ 5 labels), CP-SAT free-label and layer
   sub-problems (exact coefficients, checked against enumeration); the
   independent verifier reproduces every UB exactly.
4. **Sensitivity** (section 9): done for $P_x$, $P_d$, finger factors and
   $\lambda_m$ (`scoring/sensitivity.py`, `results/phase4/sensitivity.json`).

### Phase 5 task list (next)

1. Installable keyboard: **Kala layouts done** (11 October 2026,
   `bangla-dh kala-export`, `results/kala-keyboards/`: Kala Goti = A,
   Kala Jhor = D); live checks in Kala and Keyman remain.
2. Typing tests with people (speed, errors, learning, comfort), including a
   check of $M$ (Shift cost) and of the B/D repeated-press rule.
3. Open owner points: D3 (fingering), C's three-press rule (only if C is
   kept), the third (conjunct) layer.
4. Optional, if a tighter certificate matters: stronger relaxations than the
   cell LP (e.g. slot-level RLT on a reduced model) or longer CP-SAT runs on
   the base-layer sub-problem.

### Phase 3 task list (done)

1. **Problem file** (`data/problem-v1.json`): searched keys and slots, fixed
   assignments (digits, US punctuation), searched symbols per style, the
   symbols left for the third layer.
2. **Styles** (`bangla/styles.py`): key-map rules for A, B, C and D (D
   needs a context-aware decoder: extend `KeyMap` or add a style-specific
   one); NFC round trip on the word lists and held-out tokens, including
   বই/দই/বউ for D; per-style typed-symbol frequencies from the Wikipedia
   token tables.
3. **J1** (`scoring/`): Shift cost $M$ as in section 6.6, in both the table
   scorer and the independent verifier; UniJoy rescored under $J_1$.
4. **Search** (`search/`): simulated annealing and iterated local search
   with delta scoring, many seeds per style; record seeds, schedules and best
   scores.
5. **Evaluation:** best layouts per style on the held-out split, against
   UniJoy, under $J_0$ and $J_1$, on the unrounded and one-decimal grids;
   results labelled "best found" (section 14).

### Phase 2 outcome

All six tasks are done; `results/phase2/REPORT.md` has the numbers. In
short: inventory of 85 placed symbols (+ ZWNJ/ZWJ tracked); Kala's conjunct
list has 11 malformed entries and 82 duplicates; the scorer matches the
analyzer port on all 15 English layouts within 1e-8 and an independent text
verifier within 1e-10; UniJoy scores $J_0 = 2.173$ on Wikipedia train
(2.193 with traditional fingering), mostly from left-index same-finger
pairs; Kala's `bn_bijoy_layout.json` is a copy of UniJoy, so there is no
Bijoy baseline yet. Phase 3 needs D2 (layer cost) first, and benefits from
D1 (`.` and ZWJ/ZWNJ, digits on the number row) and D4.

### Phase 2 task list (done)

1. **Inventory** (`bangla/inventory.py`, `data/bangla-symbols-v1.json`): build
   from Kala's `Alphabet.json` and `conjuncts.json`. Validate every symbol by
   Unicode block and category, drop non-Bengali code points, and fix the NFC
   form of ড় ঢ় য়. Test: inventory hash, round trip.
2. **Typing grammar** (`bangla/grammar.py`): encode text into symbol units
   (independent vowel vs vowel sign, hasant sequences, nukta, ZWJ/ZWNJ) and
   decode back. Test the NFC invariant of section 4.1 on the corpus sample
   and on Kala's evaluation word lists.
3. **Corpus** (`corpus/`): extract documents from the bnwiki-atomic dump;
   normalize to NFC; deduplicate; split train/held-out by document; record a
   manifest. Add BanLemma text as a second domain.
4. **Frequencies** (`corpus/frequency.py`): $u_i$ and $v_{ij}$ over typing
   units with space explicit and no cross-document pairs; binary64; hashed
   outputs.
5. **Bangla scorer** (`scoring/`): $J_0$ on the ANSI model grid, with an
   independent verifier. Cross-check: on the English layouts and
   `en_books.freq` (where the caseless-script quirk does not arise) it must
   reproduce the analyzer port within binary32 tolerance.
6. **Baselines:** score Kala's UniJoy and Bijoy fixed layouts (virtual-key
   maps in `kala/layout/bn/`) under $J_0$. Avro is phonetic and is not a key
   map.

## 14. Classification of results

| Classification | Evidence required |
| --- | --- |
| Best found | Lowest score among layouts tested by the specified search |
| Bounded near-optimum | Valid upper and lower bounds with a reported gap |
| Proven optimal | Lower bound equals the solution's cost for the complete stated search space |

The aim is a keyboard whose advantages are measurable, reproducible, robust
and independently testable.

## 15. Changelog

**Experimental search season e4 (13 October 2026)**, joint J1/movement search:

* Added an isolated search track under `results/evaluator-e4/`. Existing found
  layouts, research phases and e1/e2/e3 results are hashed and preserved;
  fresh runs require new output directories. The official reproduction lock,
  challenge DATA_VERSION, leaderboard and website layout scores are unchanged.
* Success requires both strictly lower exact J1 and strictly lower key–space–key
  same-finger different-physical-key endpoint rate than the same-style published
  map. Both objectives normalize each training source independently and use the
  original 50/50 Wikipedia/newspaper mix and model-optimal fingering. Same-key
  repeats remain separate; J1, Shift costs and frozen constants are unchanged.
* Seeded annealing and ILS explore relative Chebyshev directions plus J1 alone,
  with cached symmetric pair-swap deltas. Directions are search parameters,
  not calibrated comfort weights. Bounded training archives preserve endpoints
  and the best observed joint-goal candidate; pruning is explicit and does not
  claim an exhaustive frontier. Candidate success uses exact fractions and an
  independent check against the official challenge scorer.
* Each run records code/input/output hashes, parameters, seeds and starts,
  atomic checkpoints, separate J1 and movement scores, original-map changes,
  and secondary Shift/repeat/Engram diagnostics on all five corpora under both
  fingerings. Held-out scores never guide search or selection; these existing
  benchmarks support exploratory checks. Resume rejects changed inputs,
  settings, code or environment and never overwrites completed runs.
* Claims remain best found; zero joint improvements is not an impossibility
  proof, and existing certificates do not transfer. Paired explanatory copy
  needs native-speaker editorial review before publication.

**Evaluation season e3 (13 October 2026)**, continuous-text diagnostics:

* Each layout retains its own frozen word encoder. A running-paragraph pass
  adds exact space-touching action triples: edge-space, key–space–key, and
  multiple-space windows (including space–one-action-word–space). Escapes,
  paragraph ends and document ends reset the stream. Supported punctuation
  remains an action; modifier presses are excluded.
* The word pass must reproduce e2 unigrams, pairs and within-word triples
  exactly. Running token frequencies and first/last-paragraph counts must
  reproduce the token table. Edge-space formulas, an independent sample
  scanner and the full uninterrupted-run window identity are checked.
* Key–space–key endpoint repeat, same-finger different-key, same-hand,
  opposite-hand and distance diagnostics are separate, unweighted statistics
  under both frozen fingerings. All spanning windows remain in denominators;
  unsupported endpoint mass receives explicit coverage bounds. No thumb
  assignment, changed Engram order formula or combined comfort score is added.
* Eight fixed layouts use all three existing held-out sources. Retained A/D
  maps reuse style-specific label counts, with training diagnostics on the
  original 50/50 mix. Existing benchmarks support exploratory comparison;
  there is no new candidate selection, search, layout or transferred proof.
* Results, timings and input/code/output hashes live in
  `results/evaluator-e3/run-v1/`. Optional challenge reports use committed
  hashed counts. Original J0/J1, DATA_VERSION, reproduction lock and official
  leaderboard remain unchanged. Paired explanatory copy needs native-speaker
  editorial review before publication.
* Pre-existing artifact packaging errors were found: `results/** text eol=lf`
  normalized bytes inside e2 gzip files and removed the manifest-pinned CRLF
  endings of evaluator CSV files. Gzip and result CSV files now have binary
  exceptions. Affected artifacts are restored only at their existing published
  SHA-256; scientific values and hashes are preserved.

**Evaluation season e2 (13 October 2026)**, additional movement comparison:

* Source-derived MIT Dvorak-7 and Engram functions are pinned at upstream commit
  `179e1c08b220ae1b02f6c425a7d1cbd1150c1db2`. Exhaustive fidelity checks cover
  1,764 pairs, 74,088 triples and all 49,152 distributed criterion-table rows.
* Eight fixed layouts and 101 retained A/D maps are scored on the existing
  benchmark sources. Primary traditional fingering preserves upstream;
  model-optimal is a separately declared adaptation. Physical-key projection
  excludes modifier effort. Missing events retain fixed-denominator 0..1
  coverage bounds, with text escapes disclosed separately.
* Dvorak-7 is the seven-criterion mean. Engram avg4 follows its pair generator's
  four-criterion formula, rather than silently using the upstream unifier's
  differently constructed composite. Triple order is separate; the partial
  learned preference audit and its evidence restrictions are preserved.
* Goti and Jhor exchange priority under traditional pair mechanics versus J1;
  their model-optimal pair bounds overlap. Windows Default leads their triple
  order diagnostic with substantial escaped-text and modifier limitations.
  The report explains components, source-specific results and training-only
  candidate trade-offs. These are modeled mechanics, not human validation.
* Optional challenge reports and paired website pages show these diagnostics.
  Published layouts, search, frozen J0/J1, challenge DATA_VERSION, reproduction
  lock and official leaderboard are unchanged. This additional evaluation
  season introduces no replacement layout season and inherits no certificates.
* New Bangla explanatory copy requires native-speaker editorial review before
  publication, as required by AGENTS.md.

**1.8 (11 October 2026)**, Kala keyboards (`results/kala-keyboards/README.md`):

* Owner: the mixed A and D layouts exported as Kala layouts, named
  **Kala Goti** (A) and **Kala Jhor** (D). `bangla-dh kala-export` writes
  Kala *fixed* layout files (`kala-goti.json`, `kala-jhor.json`) with an
  `about` block for Kala's layout page: how to type, search and corpus
  facts, held-out scores and a leaderboard against every fixed market layout
  tested (score 100 = lowest effort; effort index UniJoy = 100).
* A uses UniJoy's ten sequences (্ + sign). D has no sequences: the file
  holds the key map and describes the context vowel rule (section 7.1) in
  `about.style.typingRule`; Kala implements the rule in code for D-style
  keyboards (owner, 11 October 2026). Until then D's vowel keys type signs.
* Checks: a port of Kala's import validation; every label on its key; for A
  a port of `FixedLayoutManager` types the research keystrokes of the top
  held-out word types exactly and agrees with the research decoder on random
  key sequences. Kala's own importer and engine (one-off xUnit run, not
  kept) accepted both files and typed 89,009 held-out words with A exactly.
* Kala's `NativeLayoutReader` now accepts an optional `about` object; it is
  kept in the runtime copy.
* Owner: both bundled with Kala as supplied layouts next to Avro Phonetic
  and UniJoy (`kala/layout/bn/KalaGoti.json`, `KalaJhor.json`, manifest ids
  `KalaGoti`, `KalaJhor`). They are copied by hand from
  `results/kala-keyboards/`; the research code still never writes into Kala.
  Re-copy after a new `kala-export`.

**1.7 (10 October 2026)**, mixed-corpus search (`results/mix-search/REPORT.md`):

* Owner: styles A and D go to typing tests, searched on Wikipedia and news
  together (D4 updated). `bangla-dh mix-optimize` searches
  0.5 × bnwiki/train + 0.5 × newspaper/train (weights per text, not per size),
  512 runs per style plus polish runs from the earlier best layouts.
* Best found mixed J1: D 1.808796 (24/512 runs), A 1.849686 (36/512); every
  polish run from the Phase 3 and news layouts reaches the same layouts. D's
  base layer is identical to Phase 3 (6 Shift labels move); A has 3 base
  changes. All 1,024 runs share 24 base letters; the last two slots go to two
  of ◌ী, চ, ছ.
* Not re-certified (Phase 4 covers the Phase 3 layouts); D3 and D6 defaults.
* Challenge kit (11 October 2026, `bangla-dh challenge-kit`,
  `results/challenge/`): a standalone scorer for the public to try to beat
  the A and D layouts on the same mixed J1, exact as rationals, with a
  generated user guide; `challenge-verify` re-checks submissions; owner's
  guide `docs/CHALLENGE_DEPLOYMENT.md`.

**1.6 (10 October 2026)**, Phase 4 (`results/phase4/REPORT.md`):

* Owner rule for repeated presses in B and D (section 7.1): a run of one
  vowel key pairs from the end (3 presses = sign + independent vowel), so
  তিনিই is typable. Implemented in `bangla.styles` and `scoring.verify`;
  Phase 3 and the cross-check regenerated (no label moved; B and D J1
  +0.0003). C unchanged.
* OR-Tools 9.14.6206 approved by the owner (optional extra `phase4`).
* Tasks 1–4 done: exact integer model, LB0, Gilmore–Lawler, certified cell
  LP, CP-SAT, exchange and sub-problem proofs, sensitivity. Every style is a
  bounded near-optimum with a 4.0–4.3 % gap; proven optimal within ≤ 5-label
  moves, the top-20 labels and the Shift layer; C proven worse than A, B, D.
* The independent verifier now counts and sums exactly (rationals), so it
  matches the integer objective with no tolerance.
* D5 default (scale $10^6$), D3 and D6 defaults used.

**1.5 (10 October 2026)**, Phase 3 cross-check (`results/phase3-crosscheck/REPORT.md`):

* Two news collections from the owner (`data/crosscheck-v1.json`): a Prothom
  Alo newspaper set and BARD. BARD shares 81 % of its sentences with the
  newspaper set, so only its 52,376 articles sharing no sentence are used
  (`bard-novel`); both scrapes glued sentences (`।স`), repaired with a space.
* The Phase 3 layouts, unchanged, score 1.7–2.7 % lower J1 on news than on
  Wikipedia; D stays first (A and B swap, within 0.0008); the gain over UniJoy
  grows (D −36 %). The Phase 3 search on newspaper/train (32 seeds) gains at
  most 0.51 % on news held-out text, and none for D.
* Baseline registry (`data/baselines/`): fixed layouts only, never phonetic
  (owner decision); every `avro-fixed` layout in `%LOCALAPPDATA%\Kala\Layouts`
  is discovered and typed with a port of Kala's `AvroFixedLayoutManager`.
  Style D is better than UniJoy and National (Jatiya) in every metric and
  better than Bornona, Probhat, Windows Default and Munir Optima in every
  effort metric (J1, J0, E1, E2, same finger, M); those four need fewer
  keystrokes per unit through two-unit keys (and Windows Default escapes 3 %
  of the text).

**1.4 (10 October 2026)**, Phase 3:

* Implemented tasks 1–5: `data/problem-v1.json`, styles A–D with
  label-only typing machines and NFC round trips, $J_1$ (D2) in every
  scorer and the verifier, seeded search, held-out evaluation; statuses
  updated in sections 1, 3, 7, 10–13.
* Settled the D open point (vowel after ্ gives the independent vowel) and
  recorded the double-tap collisions (তিনিই in B and D, এএফসি in C) as an
  owner point before Phase 5.
* D3 and D6 defaults used (model-optimal grid, middle–index benefit kept).

**1.3 (10 October 2026)**, owner decisions:

* D1: two layers on the 26 letter keys (52 slots), digits on the number row
  and keypad, US punctuation fixed, no ZWNJ/ZWJ keys, ্ on its own key; ঽ ॥ —
  wait for the third (conjunct) layer.
* D2: Shift costs the other hand's Shift key from the model grid ($J_1$).
* D4: Wikipedia only.
* Vowel entry: four styles (A UniJoy-style, B sign double tap, C vowel
  double tap, D context) searched and compared (section 7.1). Typing units
  are counted per keystroke, conjuncts only as statistics.
* Phase 3 has not started; the owner will start it.

**1.2 (10 October 2026)**, Phase 2:

* Implemented tasks 1–6 with the default of every open decision; statuses
  updated in sections 1, 3, 5, 10–13.
* Rule: the research reads Kala's data but writes only inside
  `colemak-bangla/` (`data/`, `results/`), enforced in code.
* Found that free layers make the $E_1$ minimum stack symbols (section 6.6),
  that hasant + vowel sign artifacts collide with UniJoy's vowel sequences
  (section 4.1), and that Kala's Bijoy file duplicates UniJoy.

**1.1 (10 October 2026)**, from Phase 1 code and tests:

* Bigram table: added the middle–index benefit (−0.2/−0.1/0.0) that the
  published results depend on.
* Effort: the analyzer reads a one-decimal grid; the Fitts formula belongs
  to an unpublished generator; P_d recovered as 1.12; contact point and
  home-key rule specified.
* Switching difficulty: the implementation uses $S_2/S_1$; the Qwpr cell is
  stale.
* Original-model properties made explicit: no space, free Shift, frequencies
  re-normalized over the layout, row difference capped at 2, repeated
  characters excluded.
* Bangla: the original tool double-counts caseless scripts; ড় ঢ় য় are NFC
  composition exclusions; Kala's conjunct list needs validation.
* Lower bound: the unigram-only bound is invalid with negative penalties;
  replaced.
* Corpus: listed the Bangla sources available in Kala and the domain gap.
* Architecture and commands: replaced the planned numbered folders with the
  implemented package and marked each command's status.
* Added open decisions D1–D6 and a concrete Phase 2 task list.

**1.0**: original research and engineering plan.


## Shared publication transition — 28 October 2026

Owner decision: adopt one provisional shared arrangement B01 (`shared-76c9b9dbfc689d0b`), with Goti (A) and Jhor (D) as typing styles. Physical/layer positions are identical; frozen vowel-entry rules differ. [Rationale](SHARED_LAYOUT.md), [publication report](../results/shared-publication-v1/REPORT.md), descriptor `data/layout-publications/shared-v1.json`.

This is a new publication/challenge season `bangla-dh-shared-challenge-v1`. It adopts the separately recorded shared experiment's +0.75% exact effort/+7.5% within-distance limits against the original same-style references on the original training mix. Frozen four-component calibration and both separately calibrated R values remain unchanged; no R sum or universal winner is introduced. B01 Goti exceeds original strict Balance v1 eligibility. Sharing's learning benefit is an intended product rationale, not an observed mechanical improvement or measured learning/speed/comfort result. Preserve cross-space regressions and relearning costs. The known held-out benchmarks remain exploratory reuse.

The old model, text locks, problem, separate searches/exports and standalone legacy J1 challenge remain intact. New release output, shared scoring bundle and lock groups are additive. Existing Phase 4 certificates do not transfer. The token bard-novel denotes non-overlapping BARD news, not literary novels; the latter wording in recent exploratory prose is a non-numerical naming error. New shared map/exports use repository MIT, while original maps retain CC0. No companion app or practice lessons are changed.


### Public naming and entry-method credit — 29 October 2026

Owner request: **Kala Layout** is the public name; B01/P01 remain research labels for the unchanged map. The homepage explains the four-billion annealing-proposal scope (not unique combinations), the retained/full-score pools and provisional selection. [Typing-style heritage and credit](TYPING_STYLES.md) records Goti's modern fixed-layout lineage in Ekushey UniJoy and Avro/OmicronLab, and prior context-vowel automation in Avro. The exact Jhor repeat rule remains as specified; no global first-invention claim is supported. This is a naming, provenance and attribution update, not a new search, model, grammar or challenge season. Generated package wording advances the script version; locked scientific values remain unchanged.

### Shared neighbourhood certification — 29 October 2026

[Shared certification](SHARED_CERTIFICATION.md) adds exhaustive coverage of every two-symbol swap and three-symbol cycle around the unchanged selected B01 map: 1,326 + 44,200 alternatives. Exact effort and conservative enclosures of the existing binary64 movement/Balance scorer exclude all 45,526 as dominators, with no ambiguous comparisons. The independent full-sum/direct-scorer witness verifier and full replay accompany the machine-readable certificate and per-candidate decisions in `results/shared-certification-v1/`.

The claim is local non-dominance under joint relaxed-policy eligibility and separate frozen R values; no combined objective, global optimum or global gap is claimed. This additive check changes no map, grammar, search inputs, scoring constants, calibration or challenge season. The original Phase 4 evidence is preserved. The reproduction lock adds a certificate group; future full shared solver bounds remain separate work.


## 29 October 2026 — published separate arrangements

The owner selects original Goti and Jhor under unchanged mixed-training J1. The active selector and CLI defaults use the original scoring season; shared/Balance experiments and certificates remain historical evidence. New Goti evidence is additive: eight billion proposals plus local search, 514/8,000 exact reproductions, no improvement. See [decision](PUBLICATION_DECISION.md) and [durable evidence](GOTI_8B.md). No objective, constants, corpus, symbol problem or native grammar changed.
