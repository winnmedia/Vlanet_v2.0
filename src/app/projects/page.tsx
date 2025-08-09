'use client';

import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { Toaster } from 'sonner';
import { ProjectList } from '@/components/projects';
import { CreateProjectModal, EditProjectModal } from '@/components/projects';
import { useProjectModals } from '@/store/project.store';
import { syncUIPreferences } from '@/store/project.store';
import { DashboardLayout } from '@/components/layout/DashboardLayout';

// QueryClient 인스턴스 생성
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5분
      gcTime: 1000 * 60 * 30, // 30분
      retry: (failureCount, error) => {
        // 401, 403 에러는 재시도하지 않음
        if (error && typeof error === 'object' && 'status' in error) {
          const status = (error as any).status;
          if (status === 401 || status === 403) {
            return false;
          }
        }
        return failureCount < 2;
      },
    },
    mutations: {
      retry: false,
    },
  },
});

// ========================================
// 메인 프로젝트 페이지 컴포넌트
// ========================================

const ProjectsPageContent: React.FC = () => {
  const {
    createModalOpen,
    editModalOpen,
    editingProjectId,
    openCreateModal,
    openEditModal,
    closeAllModals,
  } = useProjectModals();

  // UI 환경설정 동기화 초기화
  React.useEffect(() => {
    syncUIPreferences();
  }, []);

  // 프로젝트 생성 성공 핸들러
  const handleCreateSuccess = (projectId: number) => {
    console.log('프로젝트가 성공적으로 생성되었습니다:', projectId);
    // 필요시 프로젝트 상세 페이지로 리다이렉트
    // router.push(`/projects/${projectId}`);
  };

  // 프로젝트 수정 성공 핸들러
  const handleEditSuccess = (project: any) => {
    console.log('프로젝트가 성공적으로 수정되었습니다:', project);
  };

  // 프로젝트 편집 핸들러
  const handleProjectEdit = (project: any) => {
    openEditModal(project.id);
  };

  // 프로젝트 삭제 핸들러
  const handleProjectDelete = (project: any) => {
    console.log('프로젝트 삭제:', project);
    // 실제로는 확인 모달을 표시하고 삭제 API 호출
  };

  // 프로젝트 복제 핸들러
  const handleProjectDuplicate = (project: any) => {
    console.log('프로젝트 복제:', project);
    // 복제 로직 구현
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 메인 컨테이너 */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 프로젝트 목록 */}
        <ProjectList
          onProjectCreate={openCreateModal}
          onProjectEdit={handleProjectEdit}
          onProjectDelete={handleProjectDelete}
          onProjectDuplicate={handleProjectDuplicate}
        />

        {/* 프로젝트 생성 모달 */}
        <CreateProjectModal
          isOpen={createModalOpen}
          onClose={closeAllModals}
          onSuccess={handleCreateSuccess}
        />

        {/* 프로젝트 수정 모달 */}
        <EditProjectModal
          isOpen={editModalOpen}
          projectId={editingProjectId}
          onClose={closeAllModals}
          onSuccess={handleEditSuccess}
          onArchive={(id) => console.log('프로젝트 보관:', id)}
          onDelete={(id) => console.log('프로젝트 삭제:', id)}
        />
      </div>

      {/* 토스트 알림 */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: 'white',
            border: '1px solid #e5e7eb',
            borderRadius: '8px',
          },
        }}
      />
    </div>
  );
};

// ========================================
// 메인 페이지 컴포넌트 (QueryClient Provider 포함)
// ========================================

export default function ProjectsPage() {
  return (
    <QueryClientProvider client={queryClient}>
      <DashboardLayout>
        <ProjectsPageContent />
      </DashboardLayout>
      
      {/* 개발 환경에서만 React Query Devtools 표시 */}
      {process.env.NODE_ENV === 'development' && (
        <ReactQueryDevtools initialIsOpen={false} />
      )}
    </QueryClientProvider>
  );
}