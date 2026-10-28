import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile, access } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { pages, homeSections, locales, sourcePath, repoRoot, rewriteLinks } from './content-map.mjs';
import { loadPublication } from './publication.mjs';

const matches = (text, regex) => [...text.matchAll(regex)].map((match) => match[1]);
const linkTargets = (text) => matches(text, /\[[^\]]*\]\(([^)]+)\)/g).sort();
const codeTokens = (text) => matches(text, /(?<!`)`([^`\n]+)`(?!`)/g).sort();
const count = (text, regex) => [...text.matchAll(regex)].length;
const rows = (text) => text.split(/\r?\n/).filter((line) => line.startsWith('|'));
const normalizeDigits = (text) => text.replace(/[০-৯]/g, (digit) => String('০১২৩৪৫৬৭৮৯'.indexOf(digit)));
const tableNumbers = (text) => rows(text).map((row) => normalizeDigits(row).match(/(?<![\p{L}])[0-9]+(?:[,.][0-9]+)*(?:e[+-]?[0-9]+)?/gu) || []);
const fences = (text) => [...text.matchAll(/^```(\w*)\r?\n([\s\S]*?)^```/gm)].map((match) => `${match[1]}\n${match[2]}`);
const keyMaps = (text) => {
  let inMap = false;
  const values = [];
  for (const row of rows(text)) {
    const cells = row.trim().replace(/^\||\|$/g, '').split('|').map((cell) => cell.trim());
    if (cells.includes('Q') && cells.includes('P') || cells.includes('A') && cells.includes('L') || cells.includes('Z') && cells.includes('M')) {
      inMap = true;
      continue;
    }
    if (inMap && cells.every((cell) => /^[-:]+$/.test(cell))) continue;
    if (inMap) {
      values.push(cells.slice(1).map((cell) => cell.normalize('NFC')));
      if (values.length % 2 === 0) inMap = false;
    }
  }
  return values;
};

export async function validateContent() {
  let links = 0;
  for (const page of [...pages, ...homeSections]) {
    const english = await readFile(sourcePath(page, 'en'), 'utf8');
    const bangla = await readFile(sourcePath(page, 'bn'), 'utf8');
    assert(/[ঀ-৿]/.test(bangla), `Bangla text missing: ${page.source}`);
    assert.deepEqual(linkTargets(bangla), linkTargets(english), `Translated link drift: ${page.source}`);
    assert.deepEqual(codeTokens(bangla), codeTokens(english), `Filename/code drift: ${page.source}`);
    assert.deepEqual(fences(bangla).filter((f) => !f.startsWith('text')), fences(english).filter((f) => !f.startsWith('text')), `Command or code block drift: ${page.source}`);
    assert.equal(count(bangla, /^#{1,6} /gm), count(english, /^#{1,6} /gm), `Heading omitted: ${page.source}`);
    assert.equal(count(bangla, /^[0-9০-৯]+\. /gm), count(english, /^\d+\. /gm), `Step omitted: ${page.source}`);
    assert.equal(count(bangla, /^\* /gm), count(english, /^\* /gm), `List item omitted: ${page.source}`);
    assert.equal(rows(bangla).length, rows(english).length, `Table row omitted: ${page.source}`);
    assert.deepEqual(tableNumbers(bangla), tableNumbers(english), `Translated table number drift: ${page.source}`);
    assert.deepEqual(keyMaps(bangla), keyMaps(english), `Translated key-map drift: ${page.source}`);
    for (const locale of locales) {
      const text = locale === 'en' ? english : bangla;
      rewriteLinks(text, page.source, locale);
      const widths = [];
      for (const line of text.split(/\r?\n/)) {
        if (!line.startsWith('|')) { widths.length = 0; continue; }
        const width = line.trim().replace(/^\||\|$/g, '').split('|').length;
        if (widths.length) assert.equal(width, widths[0], `Malformed table: ${page.source} (${locale})`);
        widths.push(width);
      }
      links += linkTargets(text).length;
    }
    // Every local link of the English source must point at a file or folder that exists.
    for (const href of linkTargets(english)) {
      if (/^(?:https?:|mailto:|#)/.test(href)) continue;
      const target = path.resolve(repoRoot, path.dirname(page.source), decodeURIComponent(href.split('#')[0]));
      await access(target).catch(() => assert.fail(`Broken repository link ${href} in ${page.source}`));
    }
  }
  await validateHomeDiagnostics();
  await validateSharedPublication();
  await validateSearchStory();
  await validateMechanics();
  await validateContinuous();
  console.log(`Content checks passed: ${pages.length + homeSections.length} complete language pairs; ${links} links; table numbers, key maps, steps, commands and paths preserved.`);
}
async function validateMechanics() {
  const source = 'results/evaluator-e2/run-v1/public-summary.json';
  const raw = await readFile(path.join(repoRoot, source));
  const manifest = JSON.parse(await readFile(path.join(repoRoot, 'results/evaluator-e2/run-v1/run-manifest.json'), 'utf8'));
  assert.equal(createHash('sha256').update(raw).digest('hex'), manifest.output_sha256[source], 'Movement scores differ from their run manifest');
  const run = JSON.parse(raw.toString('utf8'));
  assert.equal(run.layout_count, 8);
  assert.equal(run.candidate_count, 101);
  assert.equal(run.source_fidelity.source_hashes_pass, true);
  assert.equal(run.corpus_scores.length, 48);
  const names = ['Kala Jhor', 'Kala Goti', 'Windows Default', 'Probhat', 'Munir Optima (uni)', 'Bornona', 'UniJoy', 'National (Jatiya)'];
  const expected = ['traditional', 'model-optimal'].map((scenario) => names.map((name) => {
    const row = run.public_summary[scenario][name];
    return [name, ...['dvorak7', 'engram_avg4', 'engram_order'].map((m) => `${row[m].lower.toFixed(6)}–${row[m].upper.toFixed(6)}`),
      `${(100*row.coverage).toFixed(3)}%`, `${(100*row.escape_share).toFixed(3)}%`];
  }));
  for (const locale of locales) {
    const markdown = await readFile(sourcePath({source: 'docs/MECHANICS.md'}, locale), 'utf8');
    const tables = rows(markdown.split('<!-- historical-mechanics -->')[1].split('<!-- continuous-e3 -->')[0]);
    assert.equal(tables.length, 20);
    const actual = [tables.slice(2, 10), tables.slice(12, 20)].map((table) => table.map((row) => row.split('|').slice(1,-1).map((cell) => normalizeDigits(cell.trim()))));
    assert.deepEqual(actual, expected, `Movement result drift: ${locale}`);
  }
}
async function validateContinuous() {
  const source = 'results/evaluator-e3/run-v1/public-summary.json';
  const raw = await readFile(path.join(repoRoot, source));
  const manifest = JSON.parse(await readFile(path.join(repoRoot, 'results/evaluator-e3/run-v1/run-manifest.json'), 'utf8'));
  assert.equal(createHash('sha256').update(raw).digest('hex'), manifest.output_sha256[source], 'Continuous scores differ from their manifest');
  const run = JSON.parse(raw.toString('utf8'));
  assert.equal(run.layout_count, 8);
  assert.equal(run.candidate_count, 101);
  assert.equal(run.corpus_scores.length, 48);
  assert.equal(run.checks.published_and_prior_seasons_preserved, true);
  for (const row of run.corpus_scores) {
    const c = row.continuous;
    assert.equal(Object.values(c.category_counts).reduce((a, b) => a + b, 0), c.total_valid_windows);
    assert.equal(c.within_word_share, c.category_counts.within_word / c.total_valid_windows);
    assert.equal(c.ranking_effect, 'none');
  }
  const names = ['Kala Jhor', 'Kala Goti', 'Windows Default', 'Probhat', 'Munir Optima (uni)', 'Bornona', 'UniJoy', 'National (Jatiya)'];
  const interval = (row, event) => row.bounds[event].lower === row.bounds[event].upper
    ? `${(100*row.bounds[event].lower).toFixed(3)}%`
    : `${(100*row.bounds[event].lower).toFixed(3)}–${(100*row.bounds[event].upper).toFixed(3)}%`;
  const expected = names.map((name) => {
    const t = run.public_summary.traditional[name];
    const m = run.public_summary['model-optimal'][name];
    return [name, `${(100*t.within_word_share).toFixed(3)}%`, interval(t, 'same_finger_different_key'),
      interval(m, 'same_finger_different_key'), interval(t, 'opposite_hand'), `${(100*t.coverage).toFixed(3)}%`];
  });
  for (const locale of locales) {
    const markdown = await readFile(sourcePath({source: 'docs/MECHANICS.md'}, locale), 'utf8');
    const section = markdown.split('<!-- continuous-e3 -->')[1];
    assert(section, `Missing continuous-text explanation: ${locale}`);
    const actual = rows(section).slice(2).map((row) => row.split('|').slice(1,-1).map((cell) => normalizeDigits(cell.trim())));
    assert.deepEqual(actual, expected, `Continuous result drift: ${locale}`);
  }
}
// Retain historical e1 evidence checks and validate current deltas independently.
async function validateHomeDiagnostics() {
  const source = 'results/evaluator-e1/run-v1/scores.json';
  const raw = await readFile(path.join(repoRoot, source));
  const manifest = JSON.parse(await readFile(path.join(repoRoot, 'results/evaluator-e1/run-v1/run-manifest.json'), 'utf8'));
  assert.equal(createHash('sha256').update(raw).digest('hex'), manifest.output_sha256[source], 'Experimental scores differ from their run manifest');
  const run = JSON.parse(raw.toString('utf8'));
  assert.equal(run.evidence.full_layout_admitted, false, 'Review homepage comfort claims before admitting a new model');
  assert.equal(run.candidates.length, 101);
  assert.equal(new Set(run.scores.filter((row) => row.public).map((row) => row.name)).size, 8);
  const { summary } = await loadPublication();
  const expected = ['J1', 'within_distance', 'cross_distance'].map(k => ['A', 'D'].map(s => {
    const v = summary.heldout_changes_vs_original_percent[s]['model-optimal'][k];
    return `${v >= 0 ? '+' : ''}${v.toFixed(3)}`;
  }));
  for (const locale of locales) {
    const markdown = await readFile(sourcePath(homeSections[0], locale), 'utf8');
    const actual = rows(markdown).slice(2).map((row) => row.split('|').slice(2, -1).map((cell) => normalizeDigits(cell.trim()).replace('%', '')));
    assert.deepEqual(actual, expected, `Homepage diagnostic drift: ${locale}`);
  }
}
async function validateSharedPublication() {
  const { summary } = await loadPublication();
  const map = JSON.parse(await readFile(path.join(repoRoot, 'results/shared-publication-v1/shared-map.json'), 'utf8'));
  const examples = JSON.parse(await readFile(path.join(repoRoot, 'results/shared-publication-v1/examples.json'), 'utf8'));
  const expectedMaps = ['QWERTYUIOP', 'ASDFGHJKL', 'ZXCVBNM'].flatMap(keys => [1,0].map(layer => [...keys].map(k => map.layout[k][layer].normalize('NFC'))));
  for (const locale of locales) {
    const layouts = await readFile(sourcePath({ source: 'docs/LAYOUTS.md' }, locale), 'utf8');
    assert.deepEqual(keyMaps(layouts), expectedMaps, `Current shared map drift: ${locale}`);
    const exampleRows = rows(layouts).filter(r => r.split('|').length === 5 && (r.includes('Shift+') || /\| [A-Z](?: [A-Z])* \|/.test(r)));
    const expectedExamples = examples.filter(r => ['আমি','কী','বই','এবং','তিনিই','আকাশ'].includes(r.text));
    assert.deepEqual(exampleRows.map(r => r.split('|').slice(1,-1).map(c => c.trim())), expectedExamples.map(r => [r.text,r.keys,r.labels]), `Typing example drift: ${locale}`);
    const mechanics = await readFile(sourcePath({ source: 'docs/MECHANICS.md' }, locale), 'utf8');
    const expected = ['A','D'].flatMap(s => ['model-optimal','traditional'].map(f => {
      const source = ['bnwiki/heldout','newspaper/heldout','bard-novel/heldout'].map(c => summary.scores[s].diagnostics[f][c]);
      const avg = k => source.reduce((sum,r) => sum+r[k],0)/3;
      return [`${s === 'A' ? 'Goti' : 'Jhor'} (${s})`, f, ...['J1','within_distance','cross_distance'].map(k => avg(k).toFixed(6)), `${avg('order_lower').toFixed(6)}–${avg('order_upper').toFixed(6)}`, `${(100*avg('escaped_share')).toFixed(3)}%`];
    }));
    assert.deepEqual(rows(mechanics.split('<!-- historical-mechanics -->')[0]).slice(2).map(r => r.split('|').slice(1,-1).map(c => c.trim())), expected, `Shared movement drift: ${locale}`);
  }
}
async function validateSearchStory() {
  const { summary, spec } = await loadPublication();
  const search = summary.search_provenance;
  const manifest = JSON.parse(await readFile(path.join(repoRoot, search.source_run, 'run-manifest.json'), 'utf8'));
  const results = JSON.parse(await readFile(path.join(repoRoot, search.source_run, 'results.json'), 'utf8'));
  assert.equal(search.starts, manifest.seeds.length);
  assert.equal(search.annealing_proposals_per_start, manifest.settings.steps);
  assert.equal(search.annealing_proposals, search.starts * search.annealing_proposals_per_start);
  assert.equal(search.annealing_proposals, 4_000_000_000);
  assert.equal(search.distinct_retained_arrangements, results.retained_pool_count);
  assert.equal(search.full_qualifying_evaluations, results.refinement.jointly_eligible_evaluations);
  assert.equal(search.leading_tradeoffs, results.jointly_eligible_frontier_count);
  for (const locale of locales) {
    const markdown = await readFile(sourcePath({ source: 'docs/HOME_SEARCH_STORY.md' }, locale), 'utf8');
    const normalized = normalizeDigits(markdown).replaceAll(',', '');
    for (const value of [search.starts, search.annealing_proposals_per_start, search.distinct_retained_arrangements, search.full_qualifying_evaluations]) {
      assert(normalized.includes(String(value)), `Homepage search provenance drift: ${value} (${locale})`);
    }
    assert(markdown.includes(locale === 'en' ? spec.public_name : spec.public_name_bn));
    assert(markdown.includes('TYPING_STYLES.md'), `Missing input-method credit link: ${locale}`);
  }
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) await validateContent();
