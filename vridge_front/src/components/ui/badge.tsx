import React from 'react';

interface BadgeProps {
  className?: string;
  variant?: 'default' | 'secondary' | 'destructive' | 'outline';
  children: React.ReactNode;
}

const badgeVariants = {
  default: 'bg-blue-600 text-white',
  secondary: 'bg-gray-100 text-gray-900',
  destructive: 'bg-red-600 text-white',
  outline: 'border border-gray-200 text-gray-900'
};

export const Badge = ({ 
  className = '', 
  variant = 'default', 
  children 
}: BadgeProps) => (
  <span className={`
    inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
    ${badgeVariants[variant]}
    ${className}
  `}>
    {children}
  </span>
);