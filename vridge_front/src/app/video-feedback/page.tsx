'use client';

import { Suspense } from 'react';
import dynamic from 'next/dynamic';

// 전체 컨텐츠를 dynamic import로 처리
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