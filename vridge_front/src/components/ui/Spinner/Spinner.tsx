'use client';

import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/cn';

const spinnerVariants = cva(
  'animate-spin rounded-full border-solid border-t-transparent',
  {
    variants: {
      size: {
        sm: 'h-4 w-4 border-2',
        default: 'h-6 w-6 border-2',
        lg: 'h-8 w-8 border-3',
        xl: 'h-12 w-12 border-4',
      },
      color: {
        default: 'border-brand-primary',
        white: 'border-white',
        gray: 'border-gray-400',
        red: 'border-red-500',
        green: 'border-green-500',
      },
    },
    defaultVariants: {
      size: 'default',
      color: 'default',
    },
  }
);

export interface SpinnerProps
  extends Omit<React.HTMLAttributes<HTMLDivElement>, 'color'>,
    VariantProps<typeof spinnerVariants> {
  label?: string;
}

const Spinner = React.forwardRef<HTMLDivElement, SpinnerProps>(
  ({ className, size, color, label, ...props }, ref) => {
    return (
      <div
        ref={ref}
        role="status"
        aria-label={label || '로딩 중'}
        className={cn('inline-block', className)}
        {...props}
      >
        <div className={cn(spinnerVariants({ size, color }))} />
        <span className="sr-only">{label || '로딩 중'}</span>
      </div>
    );
  }
);

Spinner.displayName = 'Spinner';

export { Spinner, spinnerVariants };