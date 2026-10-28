import assert from 'node:assert/strict';
import { readdir, readFile, stat } from 'node:fs/promises';
import path from 'node:path';
import { siteRoot, base, locales, pages, generatedRoutes } from './content-map.mjs';

const root = path.join(siteRoot, 'dist');
async function walk(dir) {
  const files = [];
  for (const item of await readdir(dir, { withFileTypes: true })) {
    const name = path.join(dir, item.name);
    files.push(...item.isDirectory() ? await walk(name) : [name]);
  }
  return files;
}
const generated = await walk(root);
const existing = new Set(generated.map((file) => file.replaceAll('\\', '/')));
let checkedLinks = 0;
const routes = ['', ...pages.map((page) => page.route), ...generatedRoutes];
for (const locale of locales) {
  for (const route of routes) {
    const file = path.join(root, locale, route, 'index.html');
    const html = await readFile(file, 'utf8');
    assert(html.includes(`lang="${locale}"`), `Wrong page language: ${file}`);
    assert.equal([...html.matchAll(/<h1\b/g)].length, 1, `Duplicate/missing page title: ${file}`);
    assert(!html.includes('This content is not available in your language yet.'), `Untranslated fallback: ${file}`);
    assert(!html.includes('এই পেজের বাংলা অনুবাদ এখনো নেই।'), `Untranslated fallback: ${file}`);
    const other = locale === 'en' ? 'bn' : 'en';
    assert(html.includes(`${base}/${other}/${route ? route + '/' : ''}`), `Missing same-page language route: ${file}`);
  }
}
for (const file of generated.filter((name) => name.endsWith('.html'))) {
  const html = await readFile(file, 'utf8');
  for (const match of html.matchAll(/\b(?:href|src)="([^"]+)"/g)) {
    const target = match[1].replaceAll('&amp;', '&');
    if (/^(?:https?:|data:|mailto:|javascript:)/.test(target) || target === '') continue;
    const url = new URL(target, `https://robispider.github.io${base}/${path.relative(root, file).replaceAll('\\', '/')}`);
    assert(url.pathname.startsWith(base + '/') || url.pathname === base, `Escaped Pages base: ${target}`);
    const relative = decodeURIComponent(url.pathname.slice(base.length)).replace(/^\//, '');
    let resolved = path.join(root, relative).replaceAll('\\', '/');
    if (resolved.endsWith('/')) resolved += 'index.html';
    if (!existing.has(resolved) && existing.has(resolved + '/index.html')) resolved += '/index.html';
    assert(existing.has(resolved), `Broken output link ${target} in ${path.relative(root, file)}`);
    if (url.hash && resolved.endsWith('.html')) {
      const destination = resolved === file.replaceAll('\\', '/') ? html : await readFile(resolved, 'utf8');
      const anchor = decodeURIComponent(url.hash.slice(1));
      assert(destination.includes(`id="${anchor}"`), `Broken heading ${target} in ${path.relative(root, file)}`);
    }
    checkedLinks++;
  }
}
assert(existing.has(path.join(root, 'pagefind/pagefind.js').replaceAll('\\', '/')), 'Missing built search index');
// Current numbers and identity come from the versioned shared publication.
const board = JSON.parse(await readFile(path.join(siteRoot, 'src/generated/board.json'), 'utf8'));
assert.equal(board.public.arrangement_id, 'shared-76c9b9dbfc689d0b');
assert.equal(board.public.physical_arrangements, 7);
assert.equal(board.public.evaluation_configurations, 8);
const home = await readFile(path.join(root, 'en/index.html'), 'utf8');
for (const row of board.public.entries) assert(home.includes(row.average.toFixed(4)), `Home page lacks a current average: ${row.name}`);
assert(home.includes('One arrangement. Two typing styles.'));
assert(!home.includes('1.8000') && !home.includes('1.8432'), 'Historical averages presented as current');
for (const locale of locales) {
  const html = await readFile(path.join(root, locale, 'index.html'), 'utf8');
  assert(html.includes('class="research-hero'), `Missing research hero: ${locale}`);
  for (const route of ['release-status/', 'guide/installation/', 'guide/learning/']) {
    assert(html.includes(`https://robispider.github.io/kala-releases/${locale}/${route}`), `Missing localized app link: ${locale}/${route}`);
  }
  const layouts = await readFile(path.join(root, locale, 'layouts/index.html'), 'utf8');
  assert(layouts.includes(`https://robispider.github.io/kala-releases/${locale}/guide/learning/`), `Key maps lack localized practice guide: ${locale}`);
  assert.equal([...html.matchAll(/<section\b[^>]*class="[^"\n]*\badditional-checks\b[^"\n]*"/g)].length, 1, `Missing/duplicate additional checks section: ${locale}`);
  assert(html.includes('https://github.com/robispider/kala-layout/blob/main/results/evaluator-e1/run-v1/REPORT.md'), `Missing experimental report link: ${locale}`);
  assert(html.includes(`${base}/${locale}/mechanics/`), `Missing localized movement comparison link: ${locale}`);
  assert(html.includes(`${base}/${locale}/shared/`), `Missing transition rationale: ${locale}`);
  const shared = await readFile(path.join(root, locale, 'shared/index.html'), 'utf8');
  for (const number of ['25.750', '43', '39']) assert(shared.includes(number), `Missing transition cost ${number}: ${locale}`);
}
assert((await stat(path.join(root, 'en/index.html'))).size > 1000);
console.log(`Site checks passed: ${locales.length * routes.length} pages; ${checkedLinks} local links/assets/anchors; language switching and search.`);
