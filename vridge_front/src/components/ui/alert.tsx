import React from 'react';
import { AlertCircle, CheckCircle, Info, XCircle } from 'lucide-react';

interface AlertProps {
  className?: string;
  variant?: 'default' | 'destructive' | 'success' | 'warning';
  children: React.ReactNode;
}

interface AlertDescriptionProps {
  className?: string;
  children: React.ReactNode;
}

const alertVariants = {
  default: {
    container: 'bg-blue-50 border-blue-200 text-blue-800',
    icon: Info
  },
  destructive: {
    container: 'bg-red-50 border-red-200 text-red-800',
    icon: XCircle
  },
  success: {
    container: 'bg-green-50 border-green-200 text-green-800',
    icon: CheckCircle
  },
  warning: {
    container: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    icon: AlertCircle
  }
};

export const Alert = ({ 
  className = '', 
  variant = 'default', 
  children 
}: AlertProps) => {
  const { container, icon: Icon } = alertVariants[variant];
  
  return (
    <div className={`
      relative w-full rounded-lg border p-4 
      ${container}
      ${className}
    `}>
      <Icon className="h-4 w-4 absolute left-4 top-4" />
      <div className="ml-7">
        {children}
      </div>
    </div>
  );
};

export const AlertDescription = ({ className = '', children }: AlertDescriptionProps) => (
  <div className={`text-sm ${className}`}>
    {children}
  </div>
);