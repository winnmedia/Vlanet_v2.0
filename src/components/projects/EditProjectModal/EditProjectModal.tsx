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
// 폼 스키마 및 타입
// ========================================

const editProjectSchema = z.object({
  title: z.string()
    .min(1, '프로젝트 제목을 입력해주세요')
    .max(200, '제목은 최대 200자까지 입력 가능합니다'),
  description: z.string()
    .min(1, '프로젝트 설명을 입력해주세요')
    .max(1000, '설명은 최대 1000자까지 입력 가능합니다'),
  start_date: z.string()
    .min(1, '시작 날짜를 입력해주세요'),
  end_date: z.string()
    .min(1, '종료 날짜를 입력해주세요'),
  status: z.enum(['planning', 'production', 'review', 'completed', 'archived'] as const),
  is_public: z.boolean().default(false),
}).refine((data) => {
  const startDate = new Date(data.start_date);
  const endDate = new Date(data.end_date);
  return endDate > startDate;
}, {
  message: '종료 날짜는 시작 날짜보다 늦어야 합니다',
  path: ['end_date'],
});

type EditProjectForm = z.infer<typeof editProjectSchema>;

// ========================================
// 스타일 및 설정
// ========================================

const statusOptions: { value: ProjectStatus; label: string; description: string; color: string }[] = [
  {
    value: 'planning',
    label: '기획 중',
    description: '아이디어 구상 및 기획 단계',
    color: 'text-blue-600 bg-blue-50 border-blue-200',
  },
  {
    value: 'production',
    label: '제작 중',
    description: '실제 촬영 및 편집 진행',
    color: 'text-orange-600 bg-orange-50 border-orange-200',
  },
  {
    value: 'review',
    label: '검토 중',
    description: '완성본 검토 및 피드백 수집',
    color: 'text-purple-600 bg-purple-50 border-purple-200',
  },
  {
    value: 'completed',
    label: '완료',
    description: '프로젝트 완료 및 배포',
    color: 'text-green-600 bg-green-50 border-green-200',
  },
];

// ========================================
// 하위 컴포넌트들
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
      label="프로젝트 상태"
      error={error}
      description="현재 프로젝트의 진행 상태를 선택해주세요"
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
      label="공개 설정"
      description="프로젝트의 공개 범위를 설정해주세요"
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
            <span className="font-medium text-gray-900">비공개</span>
          </div>
          <p className="text-sm text-gray-600">
            초대된 멤버만 접근 가능
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
            <span className="font-medium text-gray-900">공개</span>
          </div>
          <p className="text-sm text-gray-600">
            누구나 볼 수 있음
          </p>
        </button>
      </div>
    </FormField>
  );
};

// ========================================
// 메인 컴포넌트
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

  // 프로젝트 데이터 조회
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

  // 폼 설정
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

  // 프로젝트 데이터로 폼 초기화
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

  // 프로젝트 수정 뮤테이션
  const updateProjectMutation = useMutation({
    mutationFn: ({ projectId, data }: { projectId: number; data: UpdateProjectRequest }) =>
      projectService.updateProject(projectId, data),
    onSuccess: (response) => {
      if (response.success && response.data) {
        // 쿼리 캐시 무효화
        queryClient.invalidateQueries({
          queryKey: projectQueryKeys.lists(),
        });
        queryClient.invalidateQueries({
          queryKey: projectQueryKeys.detail(projectId!),
        });

        toast.success('프로젝트가 성공적으로 수정되었습니다!');
        
        onClose();
        onSuccess?.(response.data);
      }
    },
    onError: (error: any) => {
      const message = error?.message || '프로젝트 수정에 실패했습니다.';
      toast.error('프로젝트 수정 실패', {
        description: message,
      });
    },
  });

  // 프로젝트 아카이브 뮤테이션
  const archiveProjectMutation = useMutation({
    mutationFn: (projectId: number) => projectService.archiveProject(projectId),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: projectQueryKeys.lists(),
      });
      toast.success('프로젝트가 보관되었습니다.');
      onClose();
      onArchive?.(projectId!);
    },
    onError: (error: any) => {
      toast.error('프로젝트 보관에 실패했습니다.');
    },
  });

  // 프로젝트 삭제 뮤테이션
  const deleteProjectMutation = useMutation({
    mutationFn: (projectId: number) => projectService.deleteProject(projectId),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: projectQueryKeys.lists(),
      });
      toast.success('프로젝트가 삭제되었습니다.');
      onClose();
      onDelete?.(projectId!);
    },
    onError: (error: any) => {
      toast.error('프로젝트 삭제에 실패했습니다.');
    },
  });

  // 폼 제출 핸들러
  const onSubmit = (data: EditProjectForm) => {
    if (!projectId) return;
    
    updateProjectMutation.mutate({
      projectId,
      data,
    });
  };

  // 아카이브 확인 핸들러
  const handleArchiveConfirm = () => {
    if (!projectId) return;
    archiveProjectMutation.mutate(projectId);
    setShowArchiveConfirm(false);
  };

  // 삭제 확인 핸들러
  const handleDeleteConfirm = () => {
    if (!projectId) return;
    deleteProjectMutation.mutate(projectId);
    setShowDeleteConfirm(false);
  };

  const isLoading = updateProjectMutation.isPending || archiveProjectMutation.isPending || deleteProjectMutation.isPending;

  // 로딩 상태
  if (isLoadingProject) {
    return (
      <Modal isOpen={isOpen} onClose={onClose} title="프로젝트 수정">
        <ModalBody className="flex items-center justify-center py-12">
          <div className="text-center">
            <Loader2 className="w-8 h-8 text-gray-400 animate-spin mx-auto mb-4" />
            <p className="text-gray-500">프로젝트 정보를 불러오는 중...</p>
          </div>
        </ModalBody>
      </Modal>
    );
  }

  // 에러 상태
  if (isProjectError || !project) {
    return (
      <Modal isOpen={isOpen} onClose={onClose} title="프로젝트 수정">
        <ModalBody className="flex items-center justify-center py-12">
          <div className="text-center">
            <AlertCircle className="w-8 h-8 text-red-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              프로젝트를 불러올 수 없습니다
            </h3>
            <p className="text-gray-500 mb-4">
              프로젝트 정보를 찾을 수 없거나 권한이 없습니다.
            </p>
            <Button onClick={onClose} variant="outline">
              닫기
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
        title={`${project.title} 수정`}
        size="lg"
        closeOnOverlayClick={!isLoading}
      >
        <form onSubmit={handleSubmit(onSubmit)}>
          <ModalBody className="space-y-6">
            {/* 프로젝트 기본 정보 */}
            <div className="space-y-4">
              <div className="border-b border-gray-200 pb-4">
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  기본 정보
                </h3>
                <p className="text-sm text-gray-600">
                  프로젝트의 기본 정보를 수정할 수 있습니다.
                </p>
              </div>

              <FormField
                label="프로젝트 제목"
                required
                error={errors.title?.message}
              >
                <Input
                  {...register('title')}
                  placeholder="프로젝트 제목"
                  className={errors.title ? 'border-red-300' : ''}
                  disabled={isLoading}
                />
              </FormField>

              <FormField
                label="프로젝트 설명"
                required
                error={errors.description?.message}
              >
                <textarea
                  {...register('description')}
                  placeholder="프로젝트 설명"
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

            {/* 일정 설정 */}
            <div className="space-y-4">
              <div className="border-b border-gray-200 pb-4">
                <h3 className="text-lg font-medium text-gray-900 mb-2 flex items-center gap-2">
                  <Calendar className="w-5 h-5" />
                  일정 설정
                </h3>
                <p className="text-sm text-gray-600">
                  프로젝트의 시작일과 종료일을 수정할 수 있습니다.
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <FormField
                  label="시작 날짜"
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
                  label="종료 날짜"
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

            {/* 상태 및 공개 설정 */}
            <div className="space-y-4">
              <div className="border-b border-gray-200 pb-4">
                <h3 className="text-lg font-medium text-gray-900 mb-2 flex items-center gap-2">
                  <Users className="w-5 h-5" />
                  프로젝트 설정
                </h3>
                <p className="text-sm text-gray-600">
                  프로젝트의 상태와 공개 범위를 수정할 수 있습니다.
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

            {/* 위험 구역 */}
            <div className="space-y-4">
              <div className="border-b border-red-200 pb-4">
                <h3 className="text-lg font-medium text-red-900 mb-2">
                  위험 구역
                </h3>
                <p className="text-sm text-red-600">
                  다음 작업들은 되돌릴 수 없습니다. 신중하게 진행해주세요.
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
                  프로젝트 보관
                </Button>

                <Button
                  type="button"
                  variant="destructive"
                  onClick={() => setShowDeleteConfirm(true)}
                  disabled={isLoading}
                  className="flex items-center gap-2"
                >
                  <Trash2 className="w-4 h-4" />
                  프로젝트 삭제
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
              취소
            </Button>
            <Button
              type="submit"
              disabled={isLoading || !isDirty}
              className="min-w-[100px]"
            >
              {isLoading ? (
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  저장 중...
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <Save className="w-4 h-4" />
                  변경사항 저장
                </div>
              )}
            </Button>
          </ModalFooter>
        </form>
      </Modal>

      {/* 아카이브 확인 모달 */}
      <ConfirmModal
        isOpen={showArchiveConfirm}
        onClose={() => setShowArchiveConfirm(false)}
        onConfirm={handleArchiveConfirm}
        title="프로젝트 보관"
        message={`"${project.title}" 프로젝트를 보관하시겠습니까? 보관된 프로젝트는 프로젝트 목록에서 숨겨지지만 언제든 복원할 수 있습니다.`}
        confirmText="보관하기"
        variant="default"
        isLoading={archiveProjectMutation.isPending}
      />

      {/* 삭제 확인 모달 */}
      <ConfirmModal
        isOpen={showDeleteConfirm}
        onClose={() => setShowDeleteConfirm(false)}
        onConfirm={handleDeleteConfirm}
        title="프로젝트 삭제"
        message={`"${project.title}" 프로젝트를 영구적으로 삭제하시겠습니까? 이 작업은 되돌릴 수 없으며, 모든 프로젝트 데이터가 삭제됩니다.`}
        confirmText="삭제하기"
        variant="destructive"
        isLoading={deleteProjectMutation.isPending}
      />
    </>
  );
};