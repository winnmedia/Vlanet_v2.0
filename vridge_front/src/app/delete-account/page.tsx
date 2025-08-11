'use client';

import React, { useState, Suspense } from 'react';
import { motion } from 'framer-motion';
import { AccountDeletionForm } from '@/components/auth/AccountDeletionForm';
import { Spinner } from '@/components/ui/Spinner';

/**
 *   
 */
function DeleteAccountPageContent() {
  const [showSuccess, setShowSuccess] = useState(false);
  const [recoveryDeadline, setRecoveryDeadline] = useState<string | null>(null);

  const handleSuccess = (deadline?: string) => {
    setRecoveryDeadline(deadline || null);
    setShowSuccess(true);
    
    // 5   
    setTimeout(() => {
      window.location.href = '/';
    }, 5000);
  };

  const handleError = (error: Error) => {
    console.error('  :', error);
  };

  const handleCancel = () => {
    //     
    window.history.back();
  };

  if (showSuccess) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="sm:mx-auto sm:w-full sm:max-w-lg"
        >
          <div className="bg-white py-8 px-4 shadow-xl sm:rounded-lg sm:px-10">
            <div className="text-center space-y-6">
              <div className="mx-auto w-20 h-20 bg-red-100 rounded-full flex items-center justify-center">
                <svg className="w-10 h-10 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              
              <div>
                <h3 className="text-2xl font-bold text-gray-900 mb-2"> </h3>
                <p className="text-gray-600">
                    .<br />
                   VideoPlanet   .
                </p>
              </div>

              {recoveryDeadline && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-left">
                  <div className="flex items-start gap-3">
                    <svg className="w-6 h-6 text-blue-500 mt-1" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                    </svg>
                    <div>
                      <h4 className="font-semibold text-blue-800 mb-2">  </h4>
                      <p className="text-sm text-blue-700 mb-3">
                           <strong>{new Date(recoveryDeadline).toLocaleDateString('ko-KR')}</strong> 
                          .
                      </p>
                      <div className="bg-blue-100 rounded p-3 text-xs text-blue-800">
                        <p className="font-medium mb-1"> :</p>
                        <ul className="space-y-1">
                          <li>• : support@vlanet.net</li>
                          <li>•      </li>
                          <li>•       </li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <p className="text-sm text-gray-600">
                  <svg className="w-4 h-4 inline mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm.707-10.293a1 1 0 00-1.414-1.414L9 7.586 7.707 6.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  5   ...
                </p>
              </div>

              <div className="space-y-3">
                <a 
                  href="/" 
                  className="inline-block w-full bg-gray-600 text-white py-3 px-4 rounded-lg hover:bg-gray-700 transition-colors"
                >
                    
                </a>
                <div className="text-sm text-gray-500">
                   VideoPlanet        .
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="sm:mx-auto sm:w-full sm:max-w-lg"
      >
        {/*  */}
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0.8 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, duration: 0.4 }}
            className="mx-auto h-12 w-12 bg-red-500 rounded-lg flex items-center justify-center mb-6"
          >
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </motion.div>
          <h2 className="text-3xl font-bold text-gray-900">VideoPlanet</h2>
          <p className="mt-2 text-gray-600"> </p>
        </div>

        {/*    */}
        <div className="bg-white py-8 px-4 shadow-xl sm:rounded-lg sm:px-10">
          <AccountDeletionForm
            onSuccess={handleSuccess}
            onError={handleError}
            onCancel={handleCancel}
          />
        </div>

        {/*  */}
        <div className="mt-6 text-center space-y-4">
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-sm text-yellow-800">
            <div className="flex items-center gap-2 mb-2">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <span className="font-medium">   </span>
            </div>
            <ul className="text-left space-y-1 text-xs">
              <li>•       </li>
              <li>• 30    </li>
              <li>•      </li>
              <li>•      </li>
            </ul>
          </div>

          <div className="space-y-2">
            <div>
              <a 
                href="/mypage" 
                className="text-sm text-gray-600 hover:text-brand-primary transition-colors"
              >
                ←  
              </a>
            </div>
            <div>
              <a 
                href="/dashboard" 
                className="text-sm text-gray-600 hover:text-brand-primary transition-colors"
              >
                 
              </a>
            </div>
            <div>
              <a 
                href="/" 
                className="text-sm text-gray-600 hover:text-brand-primary transition-colors"
              >
                 
              </a>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}

export default function DeleteAccountPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <Spinner size="lg" />
      </div>
    }>
      <DeleteAccountPageContent />
    </Suspense>
  );
}