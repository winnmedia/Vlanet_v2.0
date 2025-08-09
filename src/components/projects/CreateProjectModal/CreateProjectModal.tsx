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
// 타입 import 제거 - 직접 API 호출을 위해
import { toast } from 'sonner';
import { formatISO } from 'date-fns';

// ========================================
// 폼 스키마 및 타입
// ========================================

const createProjectSchema = z.object({
  name: z.string()
    .min(1, '프로젝트 이름을 입력해주세요')
    .max(200, '이름은 최대 200자까지 입력 가능합니다'),
  description: z.string()
    .min(1, '프로젝트 설명을 입력해주세요')
    .max(1000, '설명은 최대 1000자까지 입력 가능합니다'),
  manager: z.string()
    .min(1, '담당자를 입력해주세요')
    .max(100, '담당자는 최대 100자까지 입력 가능합니다'),
  consumer: z.string()
    .min(1, '의뢰자/고객사를 입력해주세요')
    .max(100, '의뢰자/고객사는 최대 100자까지 입력 가능합니다'),
  start_date: z.string()
    .min(1, '시작 날짜를 입력해주세요')
    .refine((date) => {
      const selectedDate = new Date(date);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      return selectedDate >= today;
    }, '시작 날짜는 오늘 이후여야 합니다'),
  end_date: z.string()
    .min(1, '종료 날짜를 입력해주세요'),
  color: z.string().default('#1631F8'),
}).refine((data) => {
  const startDate = new Date(data.start_date);
  const endDate = new Date(data.end_date);
  return endDate > startDate;
}, {
  message: '종료 날짜는 시작 날짜보다 늦어야 합니다',
  path: ['end_date'],
});

type CreateProjectForm = z.infer<typeof createProjectSchema>;

// ========================================
// 스타일 및 설정
// ========================================

// 프로젝트 진행 단계 옵션
const processSteps = [
  { key: 'basic_plan', label: '기획', description: '프로젝트 기획 및 컨셉 설정' },
  { key: 'story_board', label: '스토리보드', description: '스토리보드 및 구성안 작성' },
  { key: 'filming', label: '촬영', description: '실제 촬영 진행' },
  { key: 'video_edit', label: '편집', description: '영상 편집 작업' },
  { key: 'post_work', label: '후반작업', description: '색보정, 사운드 등 후반작업' },
  { key: 'video_preview', label: '시사', description: '완성본 시사 및 확인' },
  { key: 'confirmation', label: '확인', description: '최종 확인 및 승인' },
  { key: 'video_delivery', label: '전달', description: '완성 영상 전달' },
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

// 사용되지 않는 컴포넌트들 제거됨

// ========================================
// 메인 컴포넌트
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
  
  // 폼 설정
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

  // 프로젝트 생성 뮤테이션
  const createProjectMutation = useMutation({
    mutationFn: async (data: CreateProjectForm) => {
      // 백엔드 API 호출을 위한 데이터 변환
      const projectData = {
        name: data.name,
        description: data.description,
        manager: data.manager,
        consumer: data.consumer,
        color: data.color,
        process: generateProcessData(data.start_date, data.end_date),
      };
      
      // 직접 API 호출
      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error('로그인이 필요합니다.');
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
        throw new Error(errorData.message || '프로젝트 생성에 실패했습니다.');
      }
      
      return response.json();
    },
    onSuccess: (response) => {
      // 쿼리 캐시 무효화
      queryClient.invalidateQueries({
        queryKey: projectQueryKeys.lists(),
      });

      toast.success('프로젝트가 성공적으로 생성되었습니다!', {
        description: `"${response.name || response.title}" 프로젝트를 시작하세요.`,
        action: {
          label: '프로젝트 보기',
          onClick: () => onSuccess?.(response.id),
        },
      });

      // 폼 리셋 및 모달 닫기
      reset();
      onClose();
      
      // 성공 콜백 호출
      onSuccess?.(response.id);
    },
    onError: (error: any) => {
      const message = error?.message || '프로젝트 생성에 실패했습니다.';
      toast.error('프로젝트 생성 실패', {
        description: message,
      });
    },
  });

  // 프로세스 데이터 생성 함수
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
      
      // 마지막 단계는 종료일에 맞춤
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

  // 폼 제출 핸들러
  const onSubmit = (data: CreateProjectForm) => {
    createProjectMutation.mutate(data);
  };

  // 모달이 닫힐 때 폼 리셋
  React.useEffect(() => {
    if (!isOpen) {
      reset();
    }
  }, [isOpen, reset]);

  // 기본 날짜 설정 (모달이 열릴 때)
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
      title="새 프로젝트 만들기"
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
                프로젝트의 기본 정보를 입력해주세요.
              </p>
            </div>

            <FormField
              label="프로젝트 이름"
              required
              error={errors.name?.message}
              description="프로젝트를 쉽게 식별할 수 있는 이름을 입력해주세요"
            >
              <Input
                {...register('name')}
                placeholder="예: 브랜드 홍보 영상 제작"
                className={errors.name ? 'border-red-300' : ''}
                disabled={isLoading}
              />
            </FormField>

            <div className="grid grid-cols-2 gap-4">
              <FormField
                label="담당자"
                required
                error={errors.manager?.message}
                description="프로젝트를 담당할 매니저"
              >
                <Input
                  {...register('manager')}
                  placeholder="예: 김철수 PD"
                  className={errors.manager ? 'border-red-300' : ''}
                  disabled={isLoading}
                />
              </FormField>

              <FormField
                label="의뢰자/고객사"
                required
                error={errors.consumer?.message}
                description="프로젝트를 의뢰한 고객"
              >
                <Input
                  {...register('consumer')}
                  placeholder="예: ABC 컴퍼니"
                  className={errors.consumer ? 'border-red-300' : ''}
                  disabled={isLoading}
                />
              </FormField>
            </div>

            <FormField
              label="프로젝트 설명"
              required
              error={errors.description?.message}
              description="프로젝트의 목적과 내용을 상세히 설명해주세요"
            >
              <textarea
                {...register('description')}
                placeholder="이 프로젝트의 목표, 내용, 기대 효과 등을 설명해주세요..."
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
                프로젝트의 시작일과 종료일을 설정해주세요.
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

          {/* 프로젝트 색상 선택 */}
          <div className="space-y-4">
            <div className="border-b border-gray-200 pb-4">
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                프로젝트 색상
              </h3>
              <p className="text-sm text-gray-600">
                프로젝트를 구분하기 위한 색상을 선택해주세요.
              </p>
            </div>

            <FormField
              label="프로젝트 색상"
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
                  선택된 색상: {watchedColor}
                </div>
              </div>
            </FormField>
          </div>

          {/* 안내 메시지 */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 w-5 h-5 bg-blue-100 rounded-full flex items-center justify-center mt-0.5">
                <Check className="w-3 h-3 text-blue-600" />
              </div>
              <div>
                <h4 className="text-sm font-medium text-blue-900 mb-1">
                  자동 생성될 프로젝트 단계들
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
                  각 단계는 설정한 기간에 맞춰 자동으로 배분됩니다.
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
            취소
          </Button>
          <Button
            type="submit"
            disabled={isLoading}
            className="min-w-[100px]"
          >
            {isLoading ? (
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                생성 중...
              </div>
            ) : (
              '프로젝트 만들기'
            )}
          </Button>
        </ModalFooter>
      </form>
    </Modal>
  );
};