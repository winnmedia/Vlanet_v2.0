'use client';

import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  Calendar, 
  Users, 
  Globe, 
  Lock, 
  AlertCircle, 
  Loader2,
  Save,
  Archive,
  Trash2
} from 'lucide-react';
import { Modal, ModalBody, ModalFooter, ConfirmModal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { cn } from '@/lib/cn';
import { projectService, projectQueryKeys } from '@/lib/api/project.service';
import type { Project, UpdateProjectRequest, ProjectStatus } from '@/types';
import { toast } from 'sonner';

// ========================================
//    
// ========================================

const editProjectSchema = z.object({
  title: z.string()
    .min(1, '  ')
    .max(200, '  200  '),
  description: z.string()
    .min(1, '  ')
    .max(1000, '  1000  '),
  start_date: z.string()
    .min(1, '  '),
  end_date: z.string()
    .min(1, '  '),
  status: z.enum(['planning', 'production', 'review', 'completed', 'archived'] as const),
  is_public: z.boolean().default(false),
}).refine((data) => {
  const startDate = new Date(data.start_date);
  const endDate = new Date(data.end_date);
  return endDate > startDate;
}, {
  message: '     ',
  path: ['end_date'],
});

type EditProjectForm = z.infer<typeof editProjectSchema>;

// ========================================
//   
// ========================================

const statusOptions: { value: ProjectStatus; label: string; description: string; color: string }[] = [
  {
    value: 'planning',
    label: ' ',
    description: '    ',
    color: 'text-blue-600 bg-blue-50 border-blue-200',
  },
  {
    value: 'production',
    label: ' ',
    description: '    ',
    color: 'text-orange-600 bg-orange-50 border-orange-200',
  },
  {
    value: 'review',
    label: ' ',
    description: '    ',
    color: 'text-purple-600 bg-purple-50 border-purple-200',
  },
  {
    value: 'completed',
    label: '',
    description: '   ',
    color: 'text-green-600 bg-green-50 border-green-200',
  },
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

interface StatusSelectorProps {
  value: ProjectStatus;
  onChange: (status: ProjectStatus) => void;
  error?: string;
}

const StatusSelector: React.FC<StatusSelectorProps> = ({
  value,
  onChange,
  error,
}) => {
  return (
    <FormField
      label=" "
      error={error}
      description="    "
    >
      <div className="grid grid-cols-2 gap-3">
        {statusOptions.map((option) => (
          <button
            key={option.value}
            type="button"
            onClick={() => onChange(option.value)}
            className={cn(
              'p-3 border rounded-lg text-left transition-all duration-200',
              'hover:border-gray-300 hover:shadow-sm',
              value === option.value
                ? 'border-blue-500 bg-blue-50 ring-1 ring-blue-200'
                : 'border-gray-200 bg-white'
            )}
          >
            <div className={cn(
              'inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium mb-2',
              option.color
            )}>
              {option.label}
            </div>
            <p className="text-sm text-gray-600">
              {option.description}
            </p>
          </button>
        ))}
      </div>
    </FormField>
  );
};

interface VisibilityToggleProps {
  value: boolean;
  onChange: (isPublic: boolean) => void;
}

const VisibilityToggle: React.FC<VisibilityToggleProps> = ({
  value,
  onChange,
}) => {
  return (
    <FormField
      label=" "
      description="   "
    >
      <div className="flex gap-3">
        <button
          type="button"
          onClick={() => onChange(false)}
          className={cn(
            'flex-1 p-3 border rounded-lg text-left transition-all duration-200',
            'hover:border-gray-300 hover:shadow-sm',
            !value
              ? 'border-blue-500 bg-blue-50 ring-1 ring-blue-200'
              : 'border-gray-200 bg-white'
          )}
        >
          <div className="flex items-center gap-2 mb-2">
            <Lock className="w-4 h-4 text-gray-600" />
            <span className="font-medium text-gray-900"></span>
          </div>
          <p className="text-sm text-gray-600">
               
          </p>
        </button>

        <button
          type="button"
          onClick={() => onChange(true)}
          className={cn(
            'flex-1 p-3 border rounded-lg text-left transition-all duration-200',
            'hover:border-gray-300 hover:shadow-sm',
            value
              ? 'border-blue-500 bg-blue-50 ring-1 ring-blue-200'
              : 'border-gray-200 bg-white'
          )}
        >
          <div className="flex items-center gap-2 mb-2">
            <Globe className="w-4 h-4 text-gray-600" />
            <span className="font-medium text-gray-900"></span>
          </div>
          <p className="text-sm text-gray-600">
               
          </p>
        </button>
      </div>
    </FormField>
  );
};

// ========================================
//  
// ========================================

export interface EditProjectModalProps {
  isOpen: boolean;
  projectId: number | null;
  onClose: () => void;
  onSuccess?: (project: Project) => void;
  onArchive?: (projectId: number) => void;
  onDelete?: (projectId: number) => void;
}

export const EditProjectModal: React.FC<EditProjectModalProps> = ({
  isOpen,
  projectId,
  onClose,
  onSuccess,
  onArchive,
  onDelete,
}) => {
  const queryClient = useQueryClient();
  const [showArchiveConfirm, setShowArchiveConfirm] = React.useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = React.useState(false);

  //   
  const {
    data: projectResponse,
    isLoading: isLoadingProject,
    isError: isProjectError,
  } = useQuery({
    queryKey: projectQueryKeys.detail(projectId!),
    queryFn: () => projectService.getProjectDetail(projectId!),
    enabled: !!projectId && isOpen,
  });

  const project = projectResponse?.success ? projectResponse.data : null;

  //  
  const {
    register,
    handleSubmit,
    watch,
    setValue,
    reset,
    formState: { errors, isDirty },
  } = useForm<EditProjectForm>({
    resolver: zodResolver(editProjectSchema),
  });

  const watchedStatus = watch('status');
  const watchedIsPublic = watch('is_public');

  //    
  React.useEffect(() => {
    if (project) {
      reset({
        title: project.title,
        description: project.description,
        start_date: project.start_date,
        end_date: project.end_date,
        status: project.status,
        is_public: project.is_public,
      });
    }
  }, [project, reset]);

  //   
  const updateProjectMutation = useMutation({
    mutationFn: ({ projectId, data }: { projectId: number; data: UpdateProjectRequest }) =>
      projectService.updateProject(projectId, data),
    onSuccess: (response) => {
      if (response.success && response.data) {
        //   
        queryClient.invalidateQueries({
          queryKey: projectQueryKeys.lists(),
        });
        queryClient.invalidateQueries({
          queryKey: projectQueryKeys.detail(projectId!),
        });

        toast.success('  !');
        
        onClose();
        onSuccess?.(response.data);
      }
    },
    onError: (error: any) => {
      const message = error?.message || '  .';
      toast.error('  ', {
        description: message,
      });
    },
  });

  //   
  const archiveProjectMutation = useMutation({
    mutationFn: (projectId: number) => projectService.archiveProject(projectId),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: projectQueryKeys.lists(),
      });
      toast.success(' .');
      onClose();
      onArchive?.(projectId!);
    },
    onError: (error: any) => {
      toast.error('  .');
    },
  });

  //   
  const deleteProjectMutation = useMutation({
    mutationFn: (projectId: number) => projectService.deleteProject(projectId),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: projectQueryKeys.lists(),
      });
      toast.success(' .');
      onClose();
      onDelete?.(projectId!);
    },
    onError: (error: any) => {
      toast.error('  .');
    },
  });

  //   
  const onSubmit = (data: EditProjectForm) => {
    if (!projectId) return;
    
    updateProjectMutation.mutate({
      projectId,
      data,
    });
  };

  //   
  const handleArchiveConfirm = () => {
    if (!projectId) return;
    archiveProjectMutation.mutate(projectId);
    setShowArchiveConfirm(false);
  };

  //   
  const handleDeleteConfirm = () => {
    if (!projectId) return;
    deleteProjectMutation.mutate(projectId);
    setShowDeleteConfirm(false);
  };

  const isLoading = updateProjectMutation.isPending || archiveProjectMutation.isPending || deleteProjectMutation.isPending;

  //  
  if (isLoadingProject) {
    return (
      <Modal isOpen={isOpen} onClose={onClose} title=" ">
        <ModalBody className="flex items-center justify-center py-12">
          <div className="text-center">
            <Loader2 className="w-8 h-8 text-gray-400 animate-spin mx-auto mb-4" />
            <p className="text-gray-500">   ...</p>
          </div>
        </ModalBody>
      </Modal>
    );
  }

  //  
  if (isProjectError || !project) {
    return (
      <Modal isOpen={isOpen} onClose={onClose} title=" ">
        <ModalBody className="flex items-center justify-center py-12">
          <div className="text-center">
            <AlertCircle className="w-8 h-8 text-red-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
                 
            </h3>
            <p className="text-gray-500 mb-4">
                    .
            </p>
            <Button onClick={onClose} variant="outline">
              
            </Button>
          </div>
        </ModalBody>
      </Modal>
    );
  }

  return (
    <>
      <Modal
        isOpen={isOpen}
        onClose={onClose}
        title={`${project.title} `}
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
                error={errors.title?.message}
              >
                <Input
                  {...register('title')}
                  placeholder=" "
                  className={errors.title ? 'border-red-300' : ''}
                  disabled={isLoading}
                />
              </FormField>

              <FormField
                label=" "
                required
                error={errors.description?.message}
              >
                <textarea
                  {...register('description')}
                  placeholder=" "
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

            {/*     */}
            <div className="space-y-4">
              <div className="border-b border-gray-200 pb-4">
                <h3 className="text-lg font-medium text-gray-900 mb-2 flex items-center gap-2">
                  <Users className="w-5 h-5" />
                   
                </h3>
                <p className="text-sm text-gray-600">
                        .
                </p>
              </div>

              <StatusSelector
                value={watchedStatus}
                onChange={(status) => setValue('status', status, { shouldDirty: true })}
                error={errors.status?.message}
              />

              <VisibilityToggle
                value={watchedIsPublic}
                onChange={(isPublic) => setValue('is_public', isPublic, { shouldDirty: true })}
              />
            </div>

            {/*   */}
            <div className="space-y-4">
              <div className="border-b border-red-200 pb-4">
                <h3 className="text-lg font-medium text-red-900 mb-2">
                   
                </h3>
                <p className="text-sm text-red-600">
                      .  .
                </p>
              </div>

              <div className="flex gap-3">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setShowArchiveConfirm(true)}
                  disabled={isLoading}
                  className="flex items-center gap-2 text-orange-600 border-orange-300 hover:bg-orange-50"
                >
                  <Archive className="w-4 h-4" />
                   
                </Button>

                <Button
                  type="button"
                  variant="destructive"
                  onClick={() => setShowDeleteConfirm(true)}
                  disabled={isLoading}
                  className="flex items-center gap-2"
                >
                  <Trash2 className="w-4 h-4" />
                   
                </Button>
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
              disabled={isLoading || !isDirty}
              className="min-w-[100px]"
            >
              {isLoading ? (
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                   ...
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <Save className="w-4 h-4" />
                   
                </div>
              )}
            </Button>
          </ModalFooter>
        </form>
      </Modal>

      {/*    */}
      <ConfirmModal
        isOpen={showArchiveConfirm}
        onClose={() => setShowArchiveConfirm(false)}
        onConfirm={handleArchiveConfirm}
        title=" "
        message={`"${project.title}"  ?         .`}
        confirmText=""
        variant="default"
        isLoading={archiveProjectMutation.isPending}
      />

      {/*    */}
      <ConfirmModal
        isOpen={showDeleteConfirm}
        onClose={() => setShowDeleteConfirm(false)}
        onConfirm={handleDeleteConfirm}
        title=" "
        message={`"${project.title}"   ?     ,    .`}
        confirmText=""
        variant="destructive"
        isLoading={deleteProjectMutation.isPending}
      />
    </>
  );
};