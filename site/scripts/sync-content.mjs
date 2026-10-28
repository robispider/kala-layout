import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { base, siteRoot, repoUrl, pages, homeSections, locales, sourcePath, rewriteLinks } from './content-map.mjs';
import { validateContent } from './validate-content.mjs';
import { loadPublication } from './publication.mjs';

await validateContent();
const { spec, summary, submissions, challenge } = await loadPublication();
const generated = path.join(siteRoot, 'src/generated');
await mkdir(generated, { recursive: true });
await writeFile(path.join(generated, 'board.json'), JSON.stringify({ public: summary, submissions, dataVersion: spec.challenge_version }));
const safe = (s) => String(s).replace(/[&<>|\[\]`*_\\]/g, c => `&#${c.charCodeAt(0)};`).replace(/[\r\n]/g, ' ');
for (const locale of locales) {
  const bn = locale === 'bn';
  const t = (en, bangla) => bn ? bangla : en;
  const digits = (s) => bn ? String(s).replace(/[0-9]/g, d => '০১২৩৪৫৬৭৮৯'[Number(d)]) : String(s);
  const fmt = (n, precision = 4) => digits(Number(n).toFixed(precision));
  const entryName = e => e.kind === 'shared-style' ? t(e.name, `B01 · ${e.style === 'A' ? 'গতি' : 'ঝড়'} স্টাইল`) : e.name;
  const section = homeSections[0];
  await writeFile(path.join(generated, `additional-checks-${locale}.md`), rewriteLinks(await readFile(sourcePath(section, locale), 'utf8'), section.source, locale));
  const contentRoot = path.join(siteRoot, 'src/content/docs', locale);
  await mkdir(contentRoot, { recursive: true });
  for (const page of pages) {
    const source = await readFile(sourcePath(page, locale), 'utf8');
    const heading = source.match(/^# (.+)\r?$/m);
    if (!heading) throw new Error(`Missing title: ${page.source} (${locale})`);
    const body = rewriteLinks(source.replace(/^# .+\r?\n/, '').trim(), page.source, locale);
    const sourceInRepo = locale === 'en' ? page.source : `translations/${locale}/${page.source}`;
    const destination = path.join(contentRoot, `${page.route}.md`);
    await mkdir(path.dirname(destination), { recursive: true });
    await writeFile(destination, `---\ntitle: ${JSON.stringify(heading[1])}\neditUrl: ${JSON.stringify(`${repoUrl}/edit/main/${sourceInRepo}`)}\n---\n\n${body}\n`);
  }
  const L = [t('One shared arrangement, two typing styles. B01 is provisional; the original separate arrangements remain in the research history.', 'একটি অভিন্ন বিন্যাস, দুটি টাইপিং স্টাইল। B01 আপাতত নির্বাচিত; আগের আলাদা বিন্যাস গবেষণার ইতিহাসে সংরক্ষিত।'), '',
    `## ${t('Previously examined held-out effort', 'আগে পরীক্ষা করা আলাদা রাখা টেক্সটে পরিশ্রম')}`, '',
    t('J1 is modeled effort per text unit, lower is better. Shared styles use model-optimal fingering; fixed baselines retain favorable recorded original effort benchmarks. Seven arrangements, eight configurations. This table does not rank the shared challenge.', 'J1 প্রতি টেক্সট এককে মডেলের পরিশ্রম; কম হলে ভালো। অভিন্ন বিন্যাসের স্টাইল মডেল-অপটিমাল আঙুল-বিন্যাসে হিসাব করা; ফিক্সড বেসলাইনের আগের অনুকূল পরিশ্রম-স্কোর রাখা হয়েছে। সাতটি বিন্যাস, আটটি কনফিগারেশন। এই সারণি অভিন্ন বিন্যাসের চ্যালেঞ্জের ক্রম নয়।'), '',
    `| ${t('Configuration', 'কনফিগারেশন')} | ${t('Wikipedia', 'উইকিপিডিয়া')} | ${t('Newspaper', 'সংবাদপত্র')} | BARD | ${t('Mean', 'গড়')} |`, '| --- | --- | --- | --- | --- |'];
  for (const e of summary.entries) L.push(`| ${entryName(e)} | ${['wikipedia', 'newspaper', 'unseenNews'].map(c => fmt(e.j1[c])).join(' | ')} | ${fmt(e.average)} |`);
  L.push('', `## ${t('Shared challenge', 'অভিন্ন বিন্যাসের চ্যালেঞ্জ')}`, '',
    t('One submitted map is scored in both Goti and Jhor. Joint eligibility comes before the two separately calibrated R values. Frontier entries are non-dominated against B01 and all eligible submissions; display order is not a combined rank.', 'একটি জমা দেওয়া ম্যাপ গতি ও ঝড় দুই স্টাইলেই হিসাব করা হয়। দুই স্টাইলে যোগ্যতা যাচাইয়ের পরে আলাদাভাবে ক্যালিব্রেট করা R দেখা হয়। ফ্রন্টিয়ারের বিন্যাস B01 ও সব যোগ্য জমার তুলনায় অপ্রভাবিত; প্রদর্শনের ক্রম কোনো সম্মিলিত র‍্যাঙ্ক নয়।'), '',
    `${t('Season', 'সিজন')}: \`${spec.challenge_version}\`.`, '',
    `| ${t('Reference', 'রেফারেন্স')} | ${t('Goti R', 'গতি R')} | ${t('Jhor R', 'ঝড় R')} |`, '| --- | --- | --- |',
    `| B01 | ${fmt(challenge.reference.training.A.balance.R, 6)} | ${fmt(challenge.reference.training.D.balance.R, 6)} |`, '',
    `| ${t('Arrangement', 'বিন্যাস')} | ${t('Author', 'জমাদাতা')} | ${t('Status', 'অবস্থা')} | ${t('Goti R', 'গতি R')} | ${t('Jhor R', 'ঝড় R')} |`, '| --- | --- | --- | --- | --- |');
  const statuses = { frontier: t('frontier', 'ফ্রন্টিয়ার'), dominated: t('dominated', 'প্রভাবিত'), ineligible: t('ineligible', 'অযোগ্য') };
  for (const e of submissions.entries) L.push(`| ${safe(e.name || e.file)} | ${safe(e.author || '—')} | ${statuses[e.status]} | ${e.R.map(v => v === null ? '—' : fmt(v, 6)).join(' | ')} |`);
  if (!submissions.entries.length) L.push('', t('No submissions yet. B02 remains a documented trade-off, not an improvement on both B01 scores.', 'এখনো কোনো জমা নেই। B02 নথিভুক্ত বিকল্প সমঝোতা; B01-এর দুই স্কোরেই উন্নতি নয়।'));
  L.push('', `[${t('Rules and submission instructions', 'নিয়ম ও জমা দেওয়ার নির্দেশনা')}](${base}/${locale}/challenge/)`, '',
    `[${t('Original separate-style J1 board (legacy)', 'আগের আলাদা স্টাইলের J1 তালিকা (পুরোনো সিজন)')}](${repoUrl}/blob/main/submissions/LEADERBOARD.md)`);
  await writeFile(path.join(contentRoot, 'leaderboard.md'), `---\ntitle: ${JSON.stringify(t('Comparisons and shared challenge', 'তুলনা ও অভিন্ন বিন্যাসের চ্যালেঞ্জ'))}\neditUrl: false\n---\n\n${L.join('\n')}\n`);
  await writeFile(path.join(contentRoot, 'index.mdx'), `---\ntitle: ${JSON.stringify(t('One arrangement. Two typing styles.', 'এক বিন্যাস। দুই টাইপিং স্টাইল।'))}\ndescription: ${JSON.stringify(t('Why Kala is moving to a shared arrangement with Goti and Jhor typing styles: evidence, trade-offs, reproduction and an open challenge.', 'গতি ও ঝড় টাইপিং স্টাইলের জন্য কালার অভিন্ন বিন্যাস: সিদ্ধান্তের কারণ, প্রমাণ, সমঝোতা, পুনরুৎপাদন ও উন্মুক্ত চ্যালেঞ্জ।'))}\ntemplate: splash\nhero: {}\neditUrl: false\n---\n\nimport LayoutHome from '../../../components/LayoutHome.astro';\n\n<LayoutHome locale="${locale}" />\n`);
}
await writeFile(path.join(siteRoot, 'src/content/docs/404.md'), `---\ntitle: "Page not found / পেজটি পাওয়া যায়নি"\neditUrl: false\n---\n\n[English homepage](${base}/en/) · [বাংলা হোমপেজ](${base}/bn/)\n`);
await writeFile(path.join(siteRoot, 'public/robots.txt'), 'User-agent: *\nAllow: /\n');
console.log(`Generated bilingual shared publication: ${spec.arrangement_id}.`);
