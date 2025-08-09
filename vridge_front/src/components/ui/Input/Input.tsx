'use client';

import React, { forwardRef } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/cn';

const inputVariants = cva(
  'flex h-10 w-full rounded-lg border bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 transition-colors duration-200',
  {
    variants: {
      variant: {
        default: 'border-gray-300 focus-visible:ring-brand-primary focus-visible:border-brand-primary',
        error: 'border-red-500 focus-visible:ring-red-500 focus-visible:border-red-500',
        success: 'border-green-500 focus-visible:ring-green-500 focus-visible:border-green-500',
      },
      size: {
        default: 'h-10 px-3',
        sm: 'h-9 px-2 text-xs',
        lg: 'h-12 px-4',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
);

export interface InputProps
  extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size'>,
    VariantProps<typeof inputVariants> {
  label?: string;
  error?: string;
  helpText?: string;
  startIcon?: React.ReactNode;
  endIcon?: React.ReactNode;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, variant, size, label, error, helpText, startIcon, endIcon, ...props }, ref) => {
    const inputVariant = error ? 'error' : variant;
    
    return (
      <div className="space-y-2">
        {label && (
          <label className="text-sm font-medium text-gray-700">
            {label}
            {props.required && <span className="text-red-500 ml-1">*</span>}
          </label>
        )}
        
        <div className="relative">
          {startIcon && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
              {startIcon}
            </div>
          )}
          
          <input
            className={cn(
              inputVariants({ variant: inputVariant, size }),
              startIcon && 'pl-10',
              endIcon && 'pr-10',
              className
            )}
            ref={ref}
            {...props}
          />
          
          {endIcon && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">
              {endIcon}
            </div>
          )}
        </div>
        
        {error && (
          <p className="text-sm text-red-500 flex items-center gap-1">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {error}
          </p>
        )}
        
        {helpText && !error && (
          <p className="text-sm text-gray-500">{helpText}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export { Input, inputVariants };