import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 *    Tailwind CSS  .
 * clsx tailwind-merge  .
 * 
 * @param inputs -     
 * @returns   
 * 
 * @example
 * cn('base-class', condition && 'conditional-class', className)
 * cn('bg-red-500', 'bg-blue-500') // 'bg-blue-500' (  )
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}