'use client';

import React, { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '@/contexts/auth.context';
import { Spinner } from '@/components/ui/Spinner';

export interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredPermissions?: string[];
  fallback?: React.ReactNode;
  redirectTo?: string;
  allowGuestAccess?: boolean;
  className?: string;
}

/**
 * Protected Route  
 *        .
 */
export function ProtectedRoute({
  children,
  requiredPermissions = [],
  fallback,
  redirectTo = '/login',
  allowGuestAccess = false,
  className,
}: ProtectedRouteProps) {
  const router = useRouter();
  const pathname = usePathname();
  const { 
    user, 
    isLoading: authLoading, 
    isAuthenticated,
    hasPermission,
    checkAuthStatus 
  } = useAuth();
  
  const [isChecking, setIsChecking] = useState(true);
  const [hasAccess, setHasAccess] = useState(false);
  const [accessDeniedReason, setAccessDeniedReason] = useState<string | null>(null);

  //   
  useEffect(() => {
    const checkAccess = async () => {
      setIsChecking(true);
      setAccessDeniedReason(null);

      try {
        //   
        await checkAuthStatus();

        //    
        if (allowGuestAccess) {
          setHasAccess(true);
          setIsChecking(false);
          return;
        }

        //   
        if (!isAuthenticated || !user) {
          setAccessDeniedReason(' ');
          setHasAccess(false);
          setIsChecking(false);
          
          //    (   )
          const returnUrl = encodeURIComponent(pathname);
          router.replace(`${redirectTo}?returnUrl=${returnUrl}`);
          return;
        }

        //  
        if (requiredPermissions.length > 0) {
          const hasRequiredPermissions = requiredPermissions.every(permission => 
            hasPermission(permission)
          );

          if (!hasRequiredPermissions) {
            setAccessDeniedReason('  ');
            setHasAccess(false);
            setIsChecking(false);
            return;
          }
        }

        //   
        setHasAccess(true);
      } catch (error) {
        console.error('    :', error);
        setAccessDeniedReason('    ');
        setHasAccess(false);
      } finally {
        setIsChecking(false);
      }
    };

    checkAccess();
  }, [
    isAuthenticated, 
    user, 
    requiredPermissions, 
    allowGuestAccess, 
    pathname,
    router,
    redirectTo,
    hasPermission,
    checkAuthStatus
  ]);

  //   
  if (authLoading || isChecking) {
    if (fallback) {
      return <>{fallback}</>;
    }

    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
          className="text-center"
        >
          <div className="mb-4">
            <Spinner size="lg" />
          </div>
          <p className="text-gray-600">  ...</p>
        </motion.div>
      </div>
    );
  }

  //    
  if (!hasAccess && accessDeniedReason) {
    if (fallback) {
      return <>{fallback}</>;
    }

    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="max-w-md mx-auto text-center"
        >
          <div className="bg-white rounded-lg shadow-lg p-8">
            <div className="w-16 h-16 mx-auto mb-4 bg-red-100 rounded-full flex items-center justify-center">
              <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            
            <h2 className="text-xl font-semibold text-gray-900 mb-2"> </h2>
            <p className="text-gray-600 mb-6">{accessDeniedReason}</p>
            
            <div className="space-y-3">
              <button
                onClick={() => router.push(redirectTo)}
                className="w-full bg-brand-primary text-white py-2 px-4 rounded-lg hover:bg-brand-primary-dark transition-colors"
              >
                
              </button>
              
              <button
                onClick={() => router.back()}
                className="w-full bg-gray-100 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-200 transition-colors"
              >
                 
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    );
  }

  //     children 
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key="protected-content"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.2 }}
        className={className}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
}

/**
 * HOC     withAuth 
 */
export function withAuth<T extends object>(
  Component: React.ComponentType<T>,
  options?: Omit<ProtectedRouteProps, 'children'>
) {
  return function AuthenticatedComponent(props: T) {
    return (
      <ProtectedRoute {...options}>
        <Component {...props} />
      </ProtectedRoute>
    );
  };
}

/**
 *    
 */
export function AdminRoute({ children, ...props }: Omit<ProtectedRouteProps, 'requiredPermissions'>) {
  return (
    <ProtectedRoute
      {...props}
      requiredPermissions={['admin']}
    >
      {children}
    </ProtectedRoute>
  );
}

/**
 *    
 */
export function RoleBasedRoute({ 
  children, 
  roles, 
  ...props 
}: Omit<ProtectedRouteProps, 'requiredPermissions'> & { roles: string[] }) {
  return (
    <ProtectedRoute
      {...props}
      requiredPermissions={roles}
    >
      {children}
    </ProtectedRoute>
  );
}