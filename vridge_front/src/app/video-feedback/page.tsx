'use client';

import { Suspense } from 'react';
import dynamic from 'next/dynamic';

// Force dynamic rendering for this page
export const dynamic = 'force-dynamic';
export const fetchCache = 'force-no-store';
export const revalidate = 0;

//   dynamic import 
const VideoFeedbackContent = dynamic(
  () => import('./VideoFeedbackContent'),
  { 
    ssr: false,
    loading: () => (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }
);

export default function VideoFeedbackPage() {
  // Ensure client-side only rendering
  if (typeof window === 'undefined') {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    }>
      <VideoFeedbackContent />
    </Suspense>
  );
}