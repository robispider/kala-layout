import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { base, siteRoot, repoRoot, repoUrl, pages, homeSections, locales, sourcePath, rewriteLinks } from './content-map.mjs';
import { validateContent } from './validate-content.mjs';
import { loadPublication } from './publication.mjs';

await validateContent();
const { spec, challenge: challengeData, submissions } = await loadPublication();

const isBn = (locale) => locale === 'bn';
const text = (locale, en, bangla) => (isBn(locale) ? bangla : en);
const digits = (value, locale) => (isBn(locale) ? String(value).replace(/[0-9]/g, (d) => '০১২৩৪৫৬৭৮৯'[Number(d)]) : String(value));

// Generated data for the home and leaderboard pages.
const generated = path.join(siteRoot, 'src/generated');
await mkdir(generated, { recursive: true });
await writeFile(path.join(generated, 'board.json'), JSON.stringify({ public: challengeData.public_layouts, submissions, dataVersion: challengeData.version }));
for (const locale of locales) {
  const section = homeSections[0];
  const markdown = await readFile(sourcePath(section, locale), 'utf8');
  await writeFile(path.join(generated, `additional-checks-${locale}.md`), rewriteLinks(markdown, section.source, locale));
}

for (const locale of locales) {
  const contentRoot = path.join(siteRoot, 'src/content/docs', locale);
  await mkdir(contentRoot, { recursive: true });
  for (const page of pages) {
    const source = await readFile(sourcePath(page, locale), 'utf8');
    const heading = source.match(/^# (.+)\r?$/m);
    if (!heading) throw new Error(`Missing title: ${page.source} (${locale})`);
    const title = heading[1];
    const body = rewriteLinks(source.replace(/^# .+\r?\n/, '').trim(), page.source, locale);
    const sourceInRepo = locale === 'en' ? page.source : `translations/${locale}/${page.source}`;
    const frontmatter = `---\ntitle: ${JSON.stringify(title)}\neditUrl: ${JSON.stringify(`${repoUrl}/edit/main/${sourceInRepo}`)}\n---\n\n`;
    const destination = path.join(contentRoot, `${page.route}.md`);
    await mkdir(path.dirname(destination), { recursive: true });
    await writeFile(destination, frontmatter + body + '\n');
  }

  // Leaderboard page.
  const columns = ['wikipedia', 'newspaper', 'unseenNews'];
  const heads = text(locale, ['Wikipedia', 'Newspaper', 'Unseen news'], ['উইকিপিডিয়া', 'সংবাদপত্র', 'নতুন সংবাদ']);
  const fmt = (n) => digits(Number(n).toFixed(4), locale);
  const L = [];
  L.push(text(locale,
    'Two boards. The first lists the layouts that were compared in the research, scored on previously examined held-out text. The second lists layouts submitted to the challenge, re-scored with the public scorer.',
    'দুটি তালিকা। প্রথমটিতে গবেষণায় তুলনা করা লেআউট আছে, যেগুলোর স্কোর আগে পরীক্ষা করা আলাদা রাখা টেক্সটে হিসাব করা হয়েছে। দ্বিতীয়টিতে চ্যালেঞ্জে জমা দেওয়া লেআউট আছে, যেগুলো প্রকাশিত স্কোরার দিয়ে আবার হিসাব করা হয়েছে।'), '');
  L.push(`## ${text(locale, 'Public layouts: held-out effort', 'প্রকাশ্য লেআউট: আলাদা রাখা টেক্সটে পরিশ্রম')}`, '');
  L.push(text(locale,
    'Modeled finger effort per character (J1); lower is better. Fixed layouts only. Existing layouts are scored at the better of two fingering grids.',
    'প্রতি অক্ষরে আঙুলের মডেল করা পরিশ্রম (J1); কম হলে ভালো। শুধু ফিক্সড লেআউট। বিদ্যমান লেআউট দুটি আঙুল-বিন্যাসের মধ্যে ভালোটিতে হিসাব করা হয়েছে।'), '');
  L.push(`| ${text(locale, 'Rank', 'অবস্থান')} | ${text(locale, 'Layout', 'লেআউট')} | ${heads.join(' | ')} | ${text(locale, 'Average', 'গড়')} |`);
  L.push(`| --- | --- | ${heads.map(() => '---').join(' | ')} | --- |`);
  [...challengeData.public_layouts.entries].sort((a, b) => a.average - b.average).forEach((e, i) => {
    L.push(`| ${digits(i + 1, locale)} | ${e.name} | ${columns.map((c) => fmt(e.j1[c])).join(' | ')} | ${fmt(e.average)} |`);
  });
  L.push('', `## ${text(locale, 'Challenge submissions', 'চ্যালেঞ্জে জমা দেওয়া লেআউট')}`, '');
  for (const style of ['D', 'A']) {
    const part = submissions?.styles?.[style];
    const ref = challengeData.styles[style].reference;
    const [numerator, denominator] = ref.J1_exact.split('/').map(Number);
    const refJ1 = (numerator / denominator).toFixed(6);
    const name = style === 'D' ? text(locale, 'Style D (Kala Jhor)', 'স্টাইল D (কালা ঝড়)') : text(locale, 'Style A (Kala Goti)', 'স্টাইল A (কালা গতি)');
    L.push(`### ${name}`, '');
    L.push(text(locale, `Reference J1: ${refJ1}.`, `রেফারেন্স J1: ${digits(refJ1, locale)}।`), '');
    if (!part || part.entries.length === 0) {
      L.push(text(locale, 'No submissions yet. The first valid layout takes the first place on this board.', 'এখনো কোনো জমা পড়েনি। প্রথম বৈধ লেআউট এই তালিকার প্রথম স্থান পাবে।'), '');
      continue;
    }
    L.push(`| ${text(locale, 'Rank', 'অবস্থান')} | ${text(locale, 'Layout', 'লেআউট')} | ${text(locale, 'Author', 'জমাদাতা')} | J1 | ${text(locale, 'Against reference', 'রেফারেন্সের তুলনায়')} | ${text(locale, 'Held-out average', 'আলাদা রাখা টেক্সটের গড়')} |`);
    L.push('| --- | --- | --- | --- | --- | --- |');
    part.entries.forEach((e, i) => {
      L.push(`| ${digits(i + 1, locale)} | ${e.name} | ${e.author || '-'} | ${digits(e.J1.toFixed(6), locale)} | ${digits(e.vs_reference_percent.toFixed(4), locale)} % | ${fmt(e.held_out_average)} |`);
    });
    L.push('');
  }
  L.push(text(locale,
    `To enter, follow the [challenge rules](${base}/${locale}/challenge/). The board is rebuilt from the files in [submissions/](${repoUrl}/tree/main/submissions).`,
    `অংশ নিতে [চ্যালেঞ্জের নিয়ম](${base}/${locale}/challenge/) অনুসরণ করুন। তালিকাটি [submissions/](${repoUrl}/tree/main/submissions) ফোল্ডারের ফাইল থেকে নতুন করে তৈরি হয়।`));
  await writeFile(path.join(contentRoot, 'leaderboard.md'),
    `---\ntitle: ${JSON.stringify(text(locale, 'Leaderboard', 'লিডারবোর্ড'))}\neditUrl: false\n---\n\n${L.join('\n')}\n`);

  const hero = {
    tagline: text(locale,
      'Kala Jhor and Kala Goti were found by a computer search under an explicit model. See how, run the search yourself, and try to beat it.',
      'কালা ঝড় ও কালা গতি একটি স্পষ্ট মডেলের অধীনে কম্পিউটার সার্চে খুঁজে পাওয়া গেছে। কীভাবে, দেখুন; নিজে সার্চ চালান; আর চাইলে এর চেয়ে ভালো লেআউট খুঁজে আনুন।'),
    image: { file: '../../../assets/kala-mascot-520.png', alt: text(locale, 'Kala’s Black Bengal goat mascot', 'কালার ব্ল্যাক বেঙ্গল ছাগলের মাসকট') },
    actions: [
      { text: text(locale, 'Take the challenge', 'চ্যালেঞ্জ নিন'), link: `${base}/${locale}/challenge/`, icon: 'rocket' },
      { text: text(locale, 'How they were found', 'কীভাবে খুঁজে পাওয়া গেল'), link: `${base}/${locale}/how/`, variant: 'secondary', icon: 'right-arrow' },
      { text: text(locale, 'বাংলায় পড়ুন', 'Read in English'), link: `${base}/${isBn(locale) ? 'en' : 'bn'}/`, variant: 'minimal', icon: 'translate' },
    ],
  };
  const title = text(locale, 'Where Kala’s layouts came from, and how to beat them.', 'কালার লেআউট কোথা থেকে এল, আর কীভাবে এর চেয়ে ভালো করা যায়।');
  const description = text(locale, 'The research behind Kala Jhor and Kala Goti: the model, the public datasets, a repeatable search and an open challenge.', 'কালা ঝড় ও কালা গতির পেছনের গবেষণা: মডেল, প্রকাশ্য ডেটাসেট, পুনরায় চালানো যায় এমন সার্চ এবং সবার জন্য খোলা চ্যালেঞ্জ।');
  await writeFile(path.join(contentRoot, 'index.mdx'),
    `---\ntitle: ${JSON.stringify(title)}\ndescription: ${JSON.stringify(description)}\ntemplate: splash\nhero: ${JSON.stringify(hero)}\neditUrl: false\n---\n\nimport LayoutHome from '../../../components/LayoutHome.astro';\n\n<LayoutHome locale="${locale}" />\n`);
}
await writeFile(path.join(siteRoot, 'src/content/docs/404.md'), `---\ntitle: "Page not found / পেজটি পাওয়া যায়নি"\neditUrl: false\n---\n\nThis address does not match a page. Return to the [English homepage](${base}/en/) or read [how the layouts were found](${base}/en/how/).\n\n<span lang="bn">এই ঠিকানায় কোনো পেজ নেই। [বাংলা হোমপেজে](${base}/bn/) ফিরুন অথবা [কীভাবে লেআউট খুঁজে পাওয়া গেল](${base}/bn/how/) পড়ুন।</span>\n`);
await mkdir(path.join(siteRoot, 'public'), { recursive: true });
await writeFile(path.join(siteRoot, 'public/robots.txt'), 'User-agent: *\nAllow: /\n');
console.log(`Generated ${(pages.length + 2) * locales.length + 1} bilingual pages for ${base}/.`);

// Explicit historical shared board: its eligibility and two R values stay separate.
const historical = await loadPublication('shared-v1');
for (const locale of locales) {
  const bn = locale === 'bn';
  const t = (en, bangla) => bn ? bangla : en;
  const ref = historical.challenge.reference;
  const lines = [t('Historical shared-map challenge. B01 remains provisional under the relaxed shared eligibility policy; R is calibrated separately for each style and must not be combined.', 'ঐতিহাসিক অভিন্ন ম্যাপের চ্যালেঞ্জ। শিথিল shared eligibility policy-তে B01 আপাতত নির্বাচিত ছিল; প্রতি স্টাইলের R আলাদা ক্যালিব্রেশনে হিসাব করা, এগুলো একত্র করা যাবে না।'), '',
    '| Map | Goti R | Jhor R |', '| --- | --- | --- |',
    `| B01 | ${ref.training.A.balance.R.toFixed(6)} | ${ref.training.D.balance.R.toFixed(6)} |`, '',
    '| Entry | Status | Goti R | Jhor R |', '| --- | --- | --- | --- |'];
  for (const entry of historical.submissions.entries) {
    const safeName = String(entry.name || entry.file).replace(/[|<>\n\r]/g, ' ');
    lines.push(`| ${safeName} | ${entry.status} | ${entry.R.map(v => v == null ? '—' : v.toFixed(6)).join(' | ')} |`);
  }
  if (!historical.submissions.entries.length) lines.push(t('No historical submissions.', 'এই সিজনে কোনো জমা নেই।'));
  lines.push('', `[${t('Historical rules', 'ঐতিহাসিক নিয়ম')}](${base}/${locale}/shared-challenge/)`);
  await writeFile(path.join(siteRoot, 'src/content/docs', locale, 'shared-leaderboard.md'), `---\ntitle: ${JSON.stringify(t('Historical shared challenge board', 'ঐতিহাসিক অভিন্ন চ্যালেঞ্জের তালিকা'))}\neditUrl: false\n---\n\n${lines.join('\n')}\n`);
}
