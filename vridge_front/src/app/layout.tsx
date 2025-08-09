import type { Metadata } from 'next';
import { Inter } from 'next/font/google';

import { Providers } from './providers';

import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: {
    default: 'VideoPlanet',
    template: '%s | VideoPlanet',
  },
  description: '영상 제작자들을 위한 통합 프로젝트 관리 플랫폼',
  keywords: [
    '영상 제작',
    '프로젝트 관리',
    '영상 기획',
    '피드백 시스템',
    '협업 도구',
  ],
  authors: [{ name: 'VideoPlanet Team' }],
  creator: 'VideoPlanet',
  openGraph: {
    type: 'website',
    locale: 'ko_KR',
    url: process.env.NEXT_PUBLIC_APP_URL || 'https://vlanet.net',
    title: 'VideoPlanet - 영상 제작자를 위한 협업 플랫폼',
    description: '영상 제작 프로젝트를 더욱 효율적으로 관리하고 협업하세요.',
    siteName: 'VideoPlanet',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'VideoPlanet',
    description: '영상 제작자들을 위한 통합 프로젝트 관리 플랫폼',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  verification: {
    google: process.env.NEXT_PUBLIC_GOOGLE_VERIFICATION,
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko" suppressHydrationWarning>
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin=""
        />
        <link
          href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css"
          rel="stylesheet"
        />
      </head>
      <body className={inter.className}>
        <Providers>
          <div id="root" className="min-h-screen bg-gray-50">
            {children}
          </div>
        </Providers>
        <div id="modal-root" />
        <div id="toast-root" />
      </body>
    </html>
  );
}