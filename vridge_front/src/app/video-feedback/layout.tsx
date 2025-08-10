import { Metadata } from 'next';

export const metadata: Metadata = {
  title: '영상 피드백 | VideoPlanet',
  description: '실시간 영상 피드백 및 협업',
};

// Force dynamic rendering for this entire route segment
export const dynamic = 'force-dynamic';
export const fetchCache = 'force-no-store';
export const revalidate = 0;
export const runtime = 'nodejs';

export default function VideoFeedbackLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}