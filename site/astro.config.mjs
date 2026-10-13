import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
  site: 'https://robispider.github.io',
  base: '/kala-layout',
  trailingSlash: 'always',
  integrations: [
    starlight({
      title: 'Kala Layout',
      description: 'How the Kala Jhor and Kala Goti Bangla keyboard layouts were found, how to repeat the search, and how to challenge them.',
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
      sidebar: [
        {
          label: 'The research', translations: { bn: 'গবেষণা' },
          items: ['how', 'layouts', 'mechanics', 'data'],
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
        { tag: 'meta', attrs: { name: 'theme-color', content: '#31583e' } },
      ],
    }),
  ],
});
