import assert from 'node:assert/strict';
import { readFile, access } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { pages, locales, sourcePath, repoRoot, rewriteLinks } from './content-map.mjs';

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
  for (const page of pages) {
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
  console.log(`Content checks passed: ${pages.length} complete language pairs; ${links} links; table numbers, key maps, steps, commands and paths preserved.`);
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) await validateContent();
