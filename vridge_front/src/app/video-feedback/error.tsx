'use client';

import { useEffect } from 'react';
import { Button } from '@/components/ui/Button';

export default function VideoFeedbackError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error('Video Feedback Page Error:', error);
  }, [error]);

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          영상 피드백 페이지 로드 중 오류가 발생했습니다
        </h2>
        <p className="text-gray-600 mb-6">
          일시적인 문제일 수 있습니다. 다시 시도해주세요.
        </p>
        <div className="space-x-4">
          <Button
            onClick={reset}
            variant="primary"
          >
            다시 시도
          </Button>
          <Button
            onClick={() => window.location.href = '/dashboard'}
            variant="outline"
          >
            대시보드로 이동
          </Button>
        </div>
        {process.env.NODE_ENV === 'development' && (
          <details className="mt-8 text-left max-w-2xl mx-auto">
            <summary className="cursor-pointer text-sm text-gray-500">
              오류 상세 정보 (개발 환경)
            </summary>
            <pre className="mt-2 text-xs bg-gray-100 p-4 rounded overflow-auto">
              {error.message}
              {error.stack}
            </pre>
          </details>
        )}
      </div>
    </div>
  );
}