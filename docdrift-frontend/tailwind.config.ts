import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './lib/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: 'var(--background)',
        text: 'var(--text)',
        primary: {
          DEFAULT: '#0F3D2E',
          hover: '#0A2B20',
          light: '#E6EFEA',
        },
        accent: {
          DEFAULT: '#B8860B',
          hover: '#996F08',
          light: '#F8F3E6',
        },
        warning: {
          DEFAULT: '#7B3F3F',
          hover: '#653333',
          light: '#F5ECEC',
        },
        border: 'var(--border)',
        study: {
          bg: '#FAF6EE',
          'bg-dark': '#161A16',
          text: '#1C2B24',
          'text-dark': '#EDE7D9',
          border: '#D9CFB8',
          'border-dark': '#2A322A',
        },
      },
      fontFamily: {
        serif: ['var(--font-fraunces)', 'Georgia', 'serif'],
        sans: ['var(--font-inter)', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
};

export default config;
