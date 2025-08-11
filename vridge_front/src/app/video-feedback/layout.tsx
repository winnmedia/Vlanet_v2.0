import { Metadata } from 'next';

export const metadata: Metadata = {
  title: '  | VideoPlanet',
  description: '    ',
};

// Force dynamic rendering for this entire route segment
export const dynamic = 'force-dynamic';
export const fetchCache = 'force-no-store';
export const revalidate = 0;

export default function VideoFeedbackLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}