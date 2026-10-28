import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
  site: 'https://robispider.github.io',
  base: '/kala-layout',
  trailingSlash: 'always',
  integrations: [
    starlight({
      title: 'Kala Layout',
      description: 'One shared Bangla key arrangement with Goti and Jhor typing styles: rationale, evidence, reproducibility and challenge.',
      defaultLocale: 'en',
      locales: {
        en: { label: 'English', lang: 'en' },
        bn: { label: 'বাংলা', lang: 'bn' },
      },
      logo: { src: './src/assets/kala-mark-256.png', alt: 'Kala', replacesTitle: false },
      favicon: '/favicon.ico',
      social: [
        { icon: 'github', label: 'kala-layout on GitHub', href: 'https://github.com/robispider/kala-layout' },
      ],
      customCss: ['./src/styles/kala.css'],
      components: { Hero: './src/components/ResearchHero.astro' },
      sidebar: [
        {
          label: 'The research', translations: { bn: 'গবেষণা' },
          items: ['shared', 'layouts', 'how', 'mechanics', 'data'],
        },
        {
          label: 'Do it yourself', translations: { bn: 'নিজে করে দেখুন' },
          items: ['reproduce', 'challenge', 'leaderboard'],
        },
        {
          label: 'Reuse', translations: { bn: 'ব্যবহারের অধিকার' },
          items: ['licenses'],
        },
      ],
      pagination: true,
      lastUpdated: false,
      head: [
        { tag: 'meta', attrs: { name: 'theme-color', content: '#245bc4' } },
      ],
    }),
  ],
});
