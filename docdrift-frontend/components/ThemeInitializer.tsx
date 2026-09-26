'use client';

import { useEffect } from 'react';

export default function ThemeInitializer() {
  useEffect(() => {
    try {
      const stored = localStorage.getItem('docdrift-theme');
      const isDark = stored ? stored === 'dark' : window.matchMedia('(prefers-color-scheme: dark)').matches;
      if (isDark) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    } catch (e) {}
  }, []);

  return null;
}
