import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * 클래스명을 조건부로 결합하고 Tailwind CSS 충돌을 해결합니다.
 * clsx와 tailwind-merge를 결합하여 사용합니다.
 * 
 * @param inputs - 클래스명 배열 또는 조건부 객체
 * @returns 최적화된 클래스명 문자열
 * 
 * @example
 * cn('base-class', condition && 'conditional-class', className)
 * cn('bg-red-500', 'bg-blue-500') // 'bg-blue-500' (마지막 것만 적용)
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}