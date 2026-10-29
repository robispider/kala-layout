import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { gunzipSync } from 'node:zlib';
import { repoRoot } from './content-map.mjs';

const read = async (file) => JSON.parse(await readFile(path.join(repoRoot, file), 'utf8'));
export async function loadPublication(season) {
  const selector = await read('data/layout-publications/current.json');
  const current = await read(selector.descriptor);
  if (season !== 'shared-v1') {
    assert.equal(current.season, 'legacy-v1');
    for (const [style, data] of Object.entries(current.styles)) {
      const bytes = await readFile(path.join(repoRoot, data.export));
      assert.equal(createHash('sha256').update(bytes).digest('hex'), data.export_sha256);
      assert.equal(createHash('sha256').update(await readFile(path.join(repoRoot, data.source))).digest('hex'), data.source_sha256);
      const original = await read(data.source);
      const exported = JSON.parse(bytes);
      for (const [symbol, slot] of Object.entries(original.best.layout)) {
        const [key, layer] = slot.split('/');
        assert.equal(exported.layers[layer === 'base' ? 'normal' : 'shift'][key.charCodeAt(0)].normalize('NFC'), symbol.normalize('NFC'));
      }
    }
    const challenge = await read(current.challenge_data);
    const submissions = await read(current.leaderboard);
    assert.equal(challenge.version, current.challenge_version);
    assert.equal(submissions.data_version, challenge.version);
    const manifest = await read('challenge/run-manifest.json');
    assert.equal(submissions.data_sha256, manifest.data_sha256);
    for (const [file, expected] of Object.entries(manifest.outputs ?? {})) {
      assert.equal(createHash('sha256').update(await readFile(path.join(repoRoot, file))).digest('hex'), expected);
    }
    return {spec: current, summary: challenge.public_layouts, submissions, challenge};
  }
  const spec = await read('data/layout-publications/shared-v1.json');
  const summary = await read(spec.summary);
  const submissions = await read(spec.leaderboard);
  const challenge = await read('challenge/shared-v1/challenge-data.json');
  for (const manifestPath of ['results/shared-publication-v1/run-manifest.json', 'challenge/shared-v1/run-manifest.json']) {
    const manifest = await read(manifestPath);
    assert(Object.values(manifest.checks).every((v) => v === true), `Failed publication checks: ${manifestPath}`);
    for (const [file, expected] of Object.entries(manifest.output_sha256)) {
      const bytes = await readFile(path.join(repoRoot, file));
      assert.equal(createHash('sha256').update(bytes).digest('hex'), expected, `Publication artifact drift: ${file}`);
    }
  }
  const raw = gunzipSync(await readFile(path.join(repoRoot, spec.challenge_data)));
  assert.equal(createHash('sha256').update(raw).digest('hex'), challenge.data_sha256, 'Scoring counts drift');
  for (const data of [summary, submissions, challenge]) {
    assert.equal(data.publication_id ?? data.version, spec.version, 'Publication identity drift');
    assert.equal(data.arrangement_id, spec.arrangement_id, 'Arrangement identity drift');
  }
  assert.equal(submissions.data_version, spec.challenge_version, 'Stale leaderboard season');
  assert.equal(challenge.version, spec.challenge_version);
  assert.equal(summary.challenge_version, spec.challenge_version);
  assert.equal(submissions.data_sha256, challenge.data_sha256, 'Stale leaderboard scores');
  assert.equal(summary.challenge_data_sha256, challenge.data_sha256, 'Stale publication scores');
  assert.equal(summary.public_name, spec.public_name, 'Stale public name');
  assert.equal(summary.public_name_bn, spec.public_name_bn, 'Stale Bangla public name');
  assert.equal(challenge.reference.name, spec.public_name, 'Stale challenge reference name');
  return { spec, summary, submissions, challenge };
}
