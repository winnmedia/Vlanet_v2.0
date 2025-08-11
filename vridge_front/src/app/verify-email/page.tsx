'use client';

import React, { useState, Suspense } from 'react';
import { motion } from 'framer-motion';
import { EmailVerificationForm } from '@/components/auth/EmailVerificationForm';
import { Spinner } from '@/components/ui/Spinner';

/**
 *   
 */
function VerifyEmailPageContent() {
  const [showSuccess, setShowSuccess] = useState(false);

  const handleSuccess = () => {
    setShowSuccess(true);
    // 3    
    setTimeout(() => {
      window.location.href = '/login';
    }, 3000);
  };

  const handleError = (error: Error) => {
    console.error('  :', error);
  };

  if (showSuccess) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="sm:mx-auto sm:w-full sm:max-w-md"
        >
          <div className="bg-white py-8 px-4 shadow-xl sm:rounded-lg sm:px-10">
            <div className="text-center space-y-6">
              <div className="mx-auto w-20 h-20 bg-green-100 rounded-full flex items-center justify-center">
                <svg className="w-10 h-10 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              </div>
              
              <div>
                <h3 className="text-2xl font-bold text-gray-900 mb-2">  !</h3>
                <p className="text-gray-600">
                     .<br />
                       .
                </p>
              </div>

              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <p className="text-sm text-green-800">
                  <svg className="w-4 h-4 inline mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  3    ...
                </p>
              </div>

              <div className="space-y-2">
                <a 
                  href="/login" 
                  className="inline-block w-full bg-brand-primary text-white py-2 px-4 rounded-lg hover:bg-brand-primary-dark transition-colors"
                >
                   
                </a>
                <a 
                  href="/dashboard" 
                  className="inline-block w-full text-brand-primary hover:text-brand-primary-dark transition-colors text-sm"
                >
                    
                </a>
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
        className="sm:mx-auto sm:w-full sm:max-w-md"
      >
        {/*  */}
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0.8 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, duration: 0.4 }}
            className="mx-auto h-12 w-12 bg-brand-primary rounded-lg flex items-center justify-center mb-6"
          >
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </motion.div>
          <h2 className="text-3xl font-bold text-gray-900">VideoPlanet</h2>
          <p className="mt-2 text-gray-600"> </p>
        </div>

        {/*    */}
        <div className="bg-white py-8 px-4 shadow-xl sm:rounded-lg sm:px-10">
          <EmailVerificationForm
            onSuccess={handleSuccess}
            onError={handleError}
            tokenType="email_verification"
          />
        </div>

        {/*  */}
        <div className="mt-6 text-center space-y-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm text-blue-800">
            <div className="flex items-center gap-2 mb-2">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
              <span className="font-medium">  </span>
            </div>
            <ul className="text-left space-y-1 text-xs">
              <li>•        </li>
              <li>•   10 </li>
              <li>•     </li>
              <li>•      </li>
            </ul>
          </div>

          <div className="space-y-2">
            <div>
              <a 
                href="/login" 
                className="text-sm text-gray-600 hover:text-brand-primary transition-colors"
              >
                  
              </a>
            </div>
            <div>
              <a 
                href="/signup" 
                className="text-sm text-gray-600 hover:text-brand-primary transition-colors"
              >
                 
              </a>
            </div>
            <div>
              <a 
                href="/" 
                className="text-sm text-gray-600 hover:text-brand-primary transition-colors"
              >
                ←  
              </a>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <Spinner size="lg" />
      </div>
    }>
      <VerifyEmailPageContent />
    </Suspense>
  );
}