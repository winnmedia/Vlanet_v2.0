'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/cn';
import type { ModalProps } from '@/types';

// ========================================
//   
// ========================================

interface ModalOverlayProps {
  isOpen: boolean;
  onClose: () => void;
  closeOnOverlayClick?: boolean;
  children: React.ReactNode;
  className?: string;
}

const ModalOverlay: React.FC<ModalOverlayProps> = ({
  isOpen,
  onClose,
  closeOnOverlayClick = true,
  children,
  className,
}) => {
  const handleOverlayClick = (e: React.MouseEvent) => {
    if (closeOnOverlayClick && e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className={cn(
            'fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm',
            className
          )}
          onClick={handleOverlayClick}
        >
          {children}
        </motion.div>
      )}
    </AnimatePresence>
  );
};

// ========================================
//   
// ========================================

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  size = 'md',
  closeOnOverlayClick = true,
  showCloseButton = true,
}) => {
  // Escape   
  React.useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  //    body  
  React.useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  const sizeClasses = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
  };

  return (
    <ModalOverlay
      isOpen={isOpen}
      onClose={onClose}
      closeOnOverlayClick={closeOnOverlayClick}
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 10 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 10 }}
        transition={{ duration: 0.2, ease: 'easeOut' }}
        className={cn(
          'bg-white rounded-xl shadow-xl border border-gray-200 w-full mx-4',
          'max-h-[90vh] overflow-hidden flex flex-col',
          sizeClasses[size]
        )}
      >
        {/*   */}
        {(title || showCloseButton) && (
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            {title && (
              <h2 className="text-xl font-semibold text-gray-900">
                {title}
              </h2>
            )}
            
            {showCloseButton && (
              <Button
                variant="ghost"
                size="icon"
                onClick={onClose}
                className="text-gray-500 hover:text-gray-700 -mr-2"
              >
                <X className="w-5 h-5" />
              </Button>
            )}
          </div>
        )}

        {/*   */}
        <div className="flex-1 overflow-y-auto">
          {children}
        </div>
      </motion.div>
    </ModalOverlay>
  );
};

// ========================================
//   
// ========================================

interface ModalBodyProps {
  children: React.ReactNode;
  className?: string;
}

export const ModalBody: React.FC<ModalBodyProps> = ({
  children,
  className,
}) => {
  return (
    <div className={cn('p-6', className)}>
      {children}
    </div>
  );
};

interface ModalFooterProps {
  children: React.ReactNode;
  className?: string;
}

export const ModalFooter: React.FC<ModalFooterProps> = ({
  children,
  className,
}) => {
  return (
    <div className={cn(
      'flex items-center justify-end gap-3 p-6 border-t border-gray-200 bg-gray-50/50',
      className
    )}>
      {children}
    </div>
  );
};

// ========================================
//   
// ========================================

interface ConfirmModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title?: string;
  message?: string;
  confirmText?: string;
  cancelText?: string;
  variant?: 'default' | 'destructive';
  isLoading?: boolean;
}

export const ConfirmModal: React.FC<ConfirmModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  title = '',
  message = '  ?',
  confirmText = '',
  cancelText = '',
  variant = 'default',
  isLoading = false,
}) => {
  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      size="sm"
      closeOnOverlayClick={!isLoading}
    >
      <ModalBody>
        <p className="text-gray-700">
          {message}
        </p>
      </ModalBody>
      
      <ModalFooter>
        <Button
          variant="outline"
          onClick={onClose}
          disabled={isLoading}
        >
          {cancelText}
        </Button>
        <Button
          variant={variant === 'destructive' ? 'destructive' : 'default'}
          onClick={onConfirm}
          disabled={isLoading}
        >
          {isLoading ? ' ...' : confirmText}
        </Button>
      </ModalFooter>
    </Modal>
  );
};