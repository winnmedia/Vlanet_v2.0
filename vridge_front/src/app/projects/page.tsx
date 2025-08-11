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

// QueryClient  
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5
      gcTime: 1000 * 60 * 30, // 30
      retry: (failureCount, error) => {
        // 401, 403   
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
//    
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

  // UI   
  React.useEffect(() => {
    syncUIPreferences();
  }, []);

  //    
  const handleCreateSuccess = (projectId: number) => {
    console.log('  :', projectId);
    //     
    // router.push(`/projects/${projectId}`);
  };

  //    
  const handleEditSuccess = (project: any) => {
    console.log('  :', project);
  };

  //   
  const handleProjectEdit = (project: any) => {
    openEditModal(project.id);
  };

  //   
  const handleProjectDelete = (project: any) => {
    console.log(' :', project);
    //      API 
  };

  //   
  const handleProjectDuplicate = (project: any) => {
    console.log(' :', project);
    //   
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/*   */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/*   */}
        <ProjectList
          onProjectCreate={openCreateModal}
          onProjectEdit={handleProjectEdit}
          onProjectDelete={handleProjectDelete}
          onProjectDuplicate={handleProjectDuplicate}
        />

        {/*    */}
        <CreateProjectModal
          isOpen={createModalOpen}
          onClose={closeAllModals}
          onSuccess={handleCreateSuccess}
        />

        {/*    */}
        <EditProjectModal
          isOpen={editModalOpen}
          projectId={editingProjectId}
          onClose={closeAllModals}
          onSuccess={handleEditSuccess}
          onArchive={(id) => console.log(' :', id)}
          onDelete={(id) => console.log(' :', id)}
        />
      </div>

      {/*   */}
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
//    (QueryClient Provider )
// ========================================

export default function ProjectsPage() {
  return (
    <QueryClientProvider client={queryClient}>
      <DashboardLayout>
        <ProjectsPageContent />
      </DashboardLayout>
      
      {/*   React Query Devtools  */}
      {process.env.NODE_ENV === 'development' && (
        <ReactQueryDevtools initialIsOpen={false} />
      )}
    </QueryClientProvider>
  );
}