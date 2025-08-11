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
                
        </h2>
        <p className="text-gray-600 mb-6">
             .  .
        </p>
        <div className="space-x-4">
          <Button
            onClick={reset}
            variant="primary"
          >
             
          </Button>
          <Button
            onClick={() => window.location.href = '/dashboard'}
            variant="outline"
          >
             
          </Button>
        </div>
        {process.env.NODE_ENV === 'development' && (
          <details className="mt-8 text-left max-w-2xl mx-auto">
            <summary className="cursor-pointer text-sm text-gray-500">
                 ( )
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