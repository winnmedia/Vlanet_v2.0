import React from 'react';

interface CardProps {
  className?: string;
  children: React.ReactNode;
}

interface CardHeaderProps {
  className?: string;
  children: React.ReactNode;
}

interface CardTitleProps {
  className?: string;
  children: React.ReactNode;
}

interface CardContentProps {
  className?: string;
  children: React.ReactNode;
}

export const Card = ({ className = '', children }: CardProps) => (
  <div className={`rounded-lg border bg-white p-6 shadow-sm ${className}`}>
    {children}
  </div>
);

export const CardHeader = ({ className = '', children }: CardHeaderProps) => (
  <div className={`flex flex-col space-y-1.5 pb-6 ${className}`}>
    {children}
  </div>
);

export const CardTitle = ({ className = '', children }: CardTitleProps) => (
  <h3 className={`text-lg font-semibold leading-none tracking-tight ${className}`}>
    {children}
  </h3>
);

export const CardContent = ({ className = '', children }: CardContentProps) => (
  <div className={`${className}`}>
    {children}
  </div>
);

export const CardDescription = ({ className = '', children }: { className?: string; children: React.ReactNode }) => (
  <p className={`text-sm text-gray-600 ${className}`}>
    {children}
  </p>
);