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
// Current publication and historical routes are independently checked.
const board = JSON.parse(await readFile(path.join(siteRoot, 'src/generated/board.json'), 'utf8'));
assert.equal(board.dataVersion, 'bangla-dh-challenge-v1');
assert.equal(board.public.entries.length, 8);
for (const locale of locales) {
  const html = await readFile(path.join(root, locale, 'index.html'), 'utf8');
  assert(html.includes('class="research-hero'), `Missing research hero: ${locale}`);
  for (const route of ['publication', 'goti-evidence', 'shared', 'certification', 'layouts', 'styles'])
    assert(html.includes(`${base}/${locale}/${route}/`), `Missing current/history route: ${locale}/${route}`);
  const certificate = await readFile(path.join(root, locale, 'certification/index.html'), 'utf8');
  for (const number of ['1,326', '44,200']) assert(certificate.includes(number), `Missing certificate scope ${number}: ${locale}`);
  const styles = await readFile(path.join(root, locale, 'styles/index.html'), 'utf8');
  for (const url of ['https://ekushey.org/keyboard-layout/ekusheyr-shadhinota-unijoy-layout/', 'https://www.omicronlab.com/avro-keyboard.html'])
    assert(styles.includes(url), `Missing primary-source credit ${url}: ${locale}`);
}
const englishHome = await readFile(path.join(root, 'en/index.html'), 'utf8');
for (const row of board.public.entries) assert(englishHome.includes(row.average.toFixed(4)), `Missing current average: ${row.name}`);
assert(englishHome.includes('Two maps. Native typing rules.'));
assert(englishHome.includes('eight billion proposals plus local search'));
assert((await stat(path.join(root, 'en/index.html'))).size > 1000);
console.log(`Site checks passed: ${locales.length * routes.length} pages; ${checkedLinks} local links/assets/anchors; language switching and search.`);
