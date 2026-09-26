import type { Metadata } from 'next';
import { Fraunces, Inter } from 'next/font/google';
import ThemeInitializer from '@/components/ThemeInitializer';
import './globals.css';

const fraunces = Fraunces({
  subsets: ['latin'],
  variable: '--font-fraunces',
  display: 'swap',
  axes: ['opsz'],
});

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'DocDrift | Reference Desk & Version Intelligence',
  description: 'Grounded developer documentation Q&A with exact source citations and version isolation.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable} ${fraunces.variable}`} suppressHydrationWarning>
      <head>
      </head>
      <body className="antialiased min-h-screen bg-study-bg text-study-text dark:bg-study-bg-dark dark:text-study-text-dark paper-grain selection:bg-accent/20 selection:text-accent transition-colors duration-150">
        <ThemeInitializer />
        {children}
      </body>
    </html>
  );
}
