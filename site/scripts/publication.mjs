import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { gunzipSync } from 'node:zlib';
import { repoRoot } from './content-map.mjs';

const read = async (file) => JSON.parse(await readFile(path.join(repoRoot, file), 'utf8'));
export async function loadPublication() {
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
  return { spec, summary, submissions, challenge };
}
