'use client';

import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Calendar, AlertCircle, Check } from 'lucide-react';
import { Modal, ModalBody, ModalFooter } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { cn } from '@/lib/cn';
import { projectService, projectQueryKeys } from '@/lib/api/project.service';
//  import  -  API  
import { toast } from 'sonner';
import { formatISO } from 'date-fns';

// ========================================
//    
// ========================================

const createProjectSchema = z.object({
  name: z.string()
    .min(1, '  ')
    .max(200, '  200  '),
  description: z.string()
    .min(1, '  ')
    .max(1000, '  1000  '),
  manager: z.string()
    .min(1, ' ')
    .max(100, '  100  '),
  consumer: z.string()
    .min(1, '/ ')
    .max(100, '/  100  '),
  start_date: z.string()
    .min(1, '  ')
    .refine((date) => {
      const selectedDate = new Date(date);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      return selectedDate >= today;
    }, '    '),
  end_date: z.string()
    .min(1, '  '),
  color: z.string().default('#1631F8'),
}).refine((data) => {
  const startDate = new Date(data.start_date);
  const endDate = new Date(data.end_date);
  return endDate > startDate;
}, {
  message: '     ',
  path: ['end_date'],
});

type CreateProjectForm = z.infer<typeof createProjectSchema>;

// ========================================
//   
// ========================================

//    
const processSteps = [
  { key: 'basic_plan', label: '', description: '    ' },
  { key: 'story_board', label: '', description: '   ' },
  { key: 'filming', label: '', description: '  ' },
  { key: 'video_edit', label: '', description: '  ' },
  { key: 'post_work', label: '', description: ',   ' },
  { key: 'video_preview', label: '', description: '   ' },
  { key: 'confirmation', label: '', description: '   ' },
  { key: 'video_delivery', label: '', description: '  ' },
];

// ========================================
//  
// ========================================

interface FormFieldProps {
  label: string;
  error?: string;
  required?: boolean;
  children: React.ReactNode;
  description?: string;
}

const FormField: React.FC<FormFieldProps> = ({
  label,
  error,
  required,
  children,
  description,
}) => {
  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>
      {children}
      {description && (
        <p className="text-xs text-gray-500">{description}</p>
      )}
      {error && (
        <p className="text-sm text-red-600 flex items-center gap-1">
          <AlertCircle className="w-3 h-3" />
          {error}
        </p>
      )}
    </div>
  );
};

//    

// ========================================
//  
// ========================================

export interface CreateProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: (projectId: number) => void;
}

export const CreateProjectModal: React.FC<CreateProjectModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
}) => {
  const queryClient = useQueryClient();
  
  //  
  const {
    register,
    handleSubmit,
    watch,
    setValue,
    reset,
    formState: { errors },
  } = useForm<CreateProjectForm>({
    resolver: zodResolver(createProjectSchema),
    defaultValues: {
      name: '',
      description: '',
      manager: '',
      consumer: '',
      start_date: '',
      end_date: '',
      color: '#1631F8',
    },
  });

  const watchedColor = watch('color');

  //   
  const createProjectMutation = useMutation({
    mutationFn: async (data: CreateProjectForm) => {
      //  API    
      const projectData = {
        name: data.name,
        description: data.description,
        manager: data.manager,
        consumer: data.consumer,
        color: data.color,
        process: generateProcessData(data.start_date, data.end_date),
      };
      
      //  API 
      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error(' .');
      }
      
      const response = await fetch('https://videoplanet.up.railway.app/api/projects/create/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(projectData),
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || '  .');
      }
      
      return response.json();
    },
    onSuccess: (response) => {
      //   
      queryClient.invalidateQueries({
        queryKey: projectQueryKeys.lists(),
      });

      toast.success('  !', {
        description: `"${response.name || response.title}"  .`,
        action: {
          label: ' ',
          onClick: () => onSuccess?.(response.id),
        },
      });

      //     
      reset();
      onClose();
      
      //   
      onSuccess?.(response.id);
    },
    onError: (error: any) => {
      const message = error?.message || '  .';
      toast.error('  ', {
        description: message,
      });
    },
  });

  //    
  const generateProcessData = (startDate: string, endDate: string) => {
    const start = new Date(startDate);
    const end = new Date(endDate);
    const totalDays = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));
    const stepDays = Math.ceil(totalDays / processSteps.length);
    
    return processSteps.map((step, index) => {
      const stepStart = new Date(start);
      stepStart.setDate(start.getDate() + (index * stepDays));
      
      const stepEnd = new Date(stepStart);
      stepEnd.setDate(stepStart.getDate() + stepDays - 1);
      
      //    
      if (index === processSteps.length - 1) {
        stepEnd.setTime(end.getTime());
      }
      
      return {
        key: step.key,
        startDate: stepStart.toISOString().split('T')[0],
        endDate: stepEnd.toISOString().split('T')[0],
      };
    });
  };

  //   
  const onSubmit = (data: CreateProjectForm) => {
    createProjectMutation.mutate(data);
  };

  //     
  React.useEffect(() => {
    if (!isOpen) {
      reset();
    }
  }, [isOpen, reset]);

  //    (  )
  React.useEffect(() => {
    if (isOpen) {
      const today = new Date();
      const nextWeek = new Date();
      nextWeek.setDate(today.getDate() + 7);
      
      setValue('start_date', formatISO(today, { representation: 'date' }));
      setValue('end_date', formatISO(nextWeek, { representation: 'date' }));
    }
  }, [isOpen, setValue]);

  const isLoading = createProjectMutation.isPending;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="  "
      size="lg"
      closeOnOverlayClick={!isLoading}
    >
      <form onSubmit={handleSubmit(onSubmit)}>
        <ModalBody className="space-y-6">
          {/*    */}
          <div className="space-y-4">
            <div className="border-b border-gray-200 pb-4">
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                 
              </h3>
              <p className="text-sm text-gray-600">
                   .
              </p>
            </div>

            <FormField
              label=" "
              required
              error={errors.name?.message}
              description="      "
            >
              <Input
                {...register('name')}
                placeholder=":    "
                className={errors.name ? 'border-red-300' : ''}
                disabled={isLoading}
              />
            </FormField>

            <div className="grid grid-cols-2 gap-4">
              <FormField
                label=""
                required
                error={errors.manager?.message}
                description="  "
              >
                <Input
                  {...register('manager')}
                  placeholder=":  PD"
                  className={errors.manager ? 'border-red-300' : ''}
                  disabled={isLoading}
                />
              </FormField>

              <FormField
                label="/"
                required
                error={errors.consumer?.message}
                description="  "
              >
                <Input
                  {...register('consumer')}
                  placeholder=": ABC "
                  className={errors.consumer ? 'border-red-300' : ''}
                  disabled={isLoading}
                />
              </FormField>
            </div>

            <FormField
              label=" "
              required
              error={errors.description?.message}
              description="    "
            >
              <textarea
                {...register('description')}
                placeholder="  , ,    ..."
                rows={4}
                className={cn(
                  'w-full px-3 py-2 border border-gray-300 rounded-md text-sm',
                  'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                  'disabled:bg-gray-50 disabled:text-gray-500',
                  'resize-none transition-colors',
                  errors.description && 'border-red-300'
                )}
                disabled={isLoading}
              />
            </FormField>
          </div>

          {/*   */}
          <div className="space-y-4">
            <div className="border-b border-gray-200 pb-4">
              <h3 className="text-lg font-medium text-gray-900 mb-2 flex items-center gap-2">
                <Calendar className="w-5 h-5" />
                 
              </h3>
              <p className="text-sm text-gray-600">
                   .
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <FormField
                label=" "
                required
                error={errors.start_date?.message}
              >
                <Input
                  type="date"
                  {...register('start_date')}
                  className={errors.start_date ? 'border-red-300' : ''}
                  disabled={isLoading}
                />
              </FormField>

              <FormField
                label=" "
                required
                error={errors.end_date?.message}
              >
                <Input
                  type="date"
                  {...register('end_date')}
                  className={errors.end_date ? 'border-red-300' : ''}
                  disabled={isLoading}
                />
              </FormField>
            </div>
          </div>

          {/*    */}
          <div className="space-y-4">
            <div className="border-b border-gray-200 pb-4">
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                 
              </h3>
              <p className="text-sm text-gray-600">
                    .
              </p>
            </div>

            <FormField
              label=" "
              error={errors.color?.message}
            >
              <div className="flex items-center gap-3">
                <input
                  type="color"
                  {...register('color')}
                  className="w-12 h-12 border border-gray-300 rounded-lg cursor-pointer disabled:opacity-50"
                  disabled={isLoading}
                />
                <div className="text-sm text-gray-600">
                   : {watchedColor}
                </div>
              </div>
            </FormField>
          </div>

          {/*   */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 w-5 h-5 bg-blue-100 rounded-full flex items-center justify-center mt-0.5">
                <Check className="w-3 h-3 text-blue-600" />
              </div>
              <div>
                <h4 className="text-sm font-medium text-blue-900 mb-1">
                     
                </h4>
                <div className="text-sm text-blue-700 grid grid-cols-2 gap-2">
                  {processSteps.map((step) => (
                    <div key={step.key} className="flex items-center gap-2">
                      <span className="w-2 h-2 bg-blue-400 rounded-full"></span>
                      {step.label}
                    </div>
                  ))}
                </div>
                <p className="text-xs text-blue-600 mt-2">
                        .
                </p>
              </div>
            </div>
          </div>
        </ModalBody>

        <ModalFooter>
          <Button
            type="button"
            variant="outline"
            onClick={onClose}
            disabled={isLoading}
          >
            
          </Button>
          <Button
            type="submit"
            disabled={isLoading}
            className="min-w-[100px]"
          >
            {isLoading ? (
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                 ...
              </div>
            ) : (
              ' '
            )}
          </Button>
        </ModalFooter>
      </form>
    </Modal>
  );
};