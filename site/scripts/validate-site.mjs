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
// The published numbers on the pages come from the challenge data: Kala Jhor first, Kala Goti second.
const board = JSON.parse(await readFile(path.join(siteRoot, 'src/generated/board.json'), 'utf8'));
const ranked = [...board.public.entries].sort((a, b) => a.average - b.average).map((entry) => entry.name);
assert.deepEqual(ranked.slice(0, 2), ['Kala Jhor', 'Kala Goti']);
const home = await readFile(path.join(root, 'en/index.html'), 'utf8');
assert(home.includes('1.8000'), 'Home page lacks the Kala Jhor average');
assert((await stat(path.join(root, 'en/index.html'))).size > 1000);
console.log(`Site checks passed: ${locales.length * routes.length} pages; ${checkedLinks} local links/assets/anchors; language switching and search.`);
