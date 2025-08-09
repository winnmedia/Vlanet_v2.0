'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { 
  LayoutGrid, 
  List, 
  Plus, 
  Search,
  Filter,
  ArrowUpDown,
  CheckSquare,
  Square,
  Loader2,
  AlertCircle,
  RefreshCw,
  Trash2,
  Archive
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { ProjectCard } from '@/components/projects/ProjectCard';
import { cn } from '@/lib/cn';
import { useProjectStore, useProjectSelection, useProjectFilters } from '@/store/project.store';
import { projectService, projectQueryKeys, ProjectQueryParams } from '@/lib/api/project.service';
import type { Project } from '@/types';

// ========================================
// 타입 정의
// ========================================

export interface ProjectListProps {
  className?: string;
  enableSelection?: boolean;
  onProjectEdit?: (project: Project) => void;
  onProjectDelete?: (project: Project) => void;
  onProjectDuplicate?: (project: Project) => void;
  onProjectCreate?: () => void;
  emptyStateContent?: React.ReactNode;
  headerActions?: React.ReactNode;
}

// ========================================
// 하위 컴포넌트들
// ========================================

interface ProjectListHeaderProps {
  projectCount: number;
  selectedCount: number;
  viewMode: 'grid' | 'list';
  searchQuery: string;
  isSearching: boolean;
  onViewModeChange: (mode: 'grid' | 'list') => void;
  onSearchChange: (query: string) => void;
  onCreateProject?: () => void;
  onToggleFilters: () => void;
  onRefresh: () => void;
  onBulkActions: {
    selectAll: () => void;
    clearSelection: () => void;
    archiveSelected: () => void;
    deleteSelected: () => void;
  };
}

const ProjectListHeader: React.FC<ProjectListHeaderProps> = ({
  projectCount,
  selectedCount,
  viewMode,
  searchQuery,
  isSearching,
  onViewModeChange,
  onSearchChange,
  onCreateProject,
  onToggleFilters,
  onRefresh,
  onBulkActions,
}) => {
  const [localSearch, setLocalSearch] = React.useState(searchQuery);
  const searchTimeoutRef = React.useRef<NodeJS.Timeout | null>(null);

  // 디바운스된 검색
  React.useEffect(() => {
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }
    
    searchTimeoutRef.current = setTimeout(() => {
      onSearchChange(localSearch);
    }, 300);

    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, [localSearch, onSearchChange]);

  return (
    <div className="flex flex-col gap-4 mb-6">
      {/* 상단 헤더 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h1 className="text-2xl font-bold text-gray-900">
            프로젝트 
            <span className="ml-2 text-sm font-normal text-gray-500">
              ({projectCount.toLocaleString()}개)
            </span>
          </h1>
          
          {selectedCount > 0 && (
            <div className="flex items-center gap-2 px-3 py-1 bg-blue-50 border border-blue-200 rounded-lg">
              <span className="text-sm text-blue-700 font-medium">
                {selectedCount}개 선택됨
              </span>
              <div className="flex items-center gap-1">
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={onBulkActions.archiveSelected}
                  className="h-6 px-2 text-xs"
                >
                  <Archive className="w-3 h-3 mr-1" />
                  보관
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={onBulkActions.deleteSelected}
                  className="h-6 px-2 text-xs text-red-600 hover:text-red-700 hover:bg-red-50"
                >
                  <Trash2 className="w-3 h-3 mr-1" />
                  삭제
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={onBulkActions.clearSelection}
                  className="h-6 px-2 text-xs"
                >
                  선택 해제
                </Button>
              </div>
            </div>
          )}
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={onRefresh}
            className="text-gray-500 hover:text-gray-700"
          >
            <RefreshCw className="w-4 h-4" />
          </Button>
          
          {onCreateProject && (
            <Button onClick={onCreateProject} className="flex items-center gap-2">
              <Plus className="w-4 h-4" />
              새 프로젝트
            </Button>
          )}
        </div>
      </div>

      {/* 검색 및 필터 바 */}
      <div className="flex items-center gap-3">
        {/* 검색 */}
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <Input
            type="text"
            placeholder="프로젝트 검색..."
            value={localSearch}
            onChange={(e) => setLocalSearch(e.target.value)}
            className="pl-10"
          />
          {isSearching && (
            <Loader2 className="absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 animate-spin" />
          )}
        </div>

        {/* 필터 버튼 */}
        <Button
          variant="outline"
          onClick={onToggleFilters}
          className="flex items-center gap-2"
        >
          <Filter className="w-4 h-4" />
          필터
        </Button>

        {/* 정렬 버튼 */}
        <Button
          variant="outline"
          className="flex items-center gap-2"
        >
          <ArrowUpDown className="w-4 h-4" />
          정렬
        </Button>

        {/* 뷰 모드 토글 */}
        <div className="flex items-center border border-gray-200 rounded-lg overflow-hidden">
          <button
            onClick={() => onViewModeChange('grid')}
            className={cn(
              'p-2 transition-colors',
              viewMode === 'grid' 
                ? 'bg-blue-50 text-blue-600' 
                : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
            )}
          >
            <LayoutGrid className="w-4 h-4" />
          </button>
          <button
            onClick={() => onViewModeChange('list')}
            className={cn(
              'p-2 transition-colors',
              viewMode === 'list' 
                ? 'bg-blue-50 text-blue-600' 
                : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
            )}
          >
            <List className="w-4 h-4" />
          </button>
        </div>

        {/* 전체 선택 */}
        <Button
          variant="ghost"
          size="icon"
          onClick={selectedCount === projectCount ? onBulkActions.clearSelection : onBulkActions.selectAll}
          className="text-gray-500 hover:text-gray-700"
        >
          {selectedCount === projectCount ? (
            <CheckSquare className="w-4 h-4" />
          ) : (
            <Square className="w-4 h-4" />
          )}
        </Button>
      </div>
    </div>
  );
};

interface ProjectGridProps {
  projects: Project[];
  viewMode: 'grid' | 'list';
  showThumbnails: boolean;
  compactMode: boolean;
  onProjectEdit?: (project: Project) => void;
  onProjectDelete?: (project: Project) => void;
  onProjectDuplicate?: (project: Project) => void;
  onProjectNavigate?: (project: Project) => void;
}

const ProjectGrid: React.FC<ProjectGridProps> = ({
  projects,
  viewMode,
  showThumbnails,
  compactMode,
  onProjectEdit,
  onProjectDelete,
  onProjectDuplicate,
  onProjectNavigate,
}) => {
  // 애니메이션 variants
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  if (viewMode === 'grid') {
    return (
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className={cn(
          'grid gap-4',
          compactMode 
            ? 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6'
            : 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4'
        )}
      >
        {projects.map((project) => (
          <ProjectCard
            key={project.id}
            project={project}
            viewMode="grid"
            showThumbnails={showThumbnails}
            compactMode={compactMode}
            onEdit={onProjectEdit}
            onDelete={onProjectDelete}
            onDuplicate={onProjectDuplicate}
            onNavigate={onProjectNavigate}
          />
        ))}
      </motion.div>
    );
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-2"
    >
      {projects.map((project) => (
        <ProjectCard
          key={project.id}
          project={project}
          viewMode="list"
          showThumbnails={showThumbnails}
          compactMode={compactMode}
          onEdit={onProjectEdit}
          onDelete={onProjectDelete}
          onDuplicate={onProjectDuplicate}
          onNavigate={onProjectNavigate}
        />
      ))}
    </motion.div>
  );
};

interface EmptyStateProps {
  hasFilters: boolean;
  onCreateProject?: () => void;
  onClearFilters: () => void;
  customContent?: React.ReactNode;
}

const EmptyState: React.FC<EmptyStateProps> = ({
  hasFilters,
  onCreateProject,
  onClearFilters,
  customContent,
}) => {
  if (customContent) {
    return <div className="text-center py-12">{customContent}</div>;
  }

  if (hasFilters) {
    return (
      <div className="text-center py-12">
        <div className="mb-4">
          <Search className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            검색 결과가 없습니다
          </h3>
          <p className="text-gray-500 mb-6">
            다른 검색어나 필터를 시도해보세요.
          </p>
        </div>
        <Button onClick={onClearFilters} variant="outline">
          필터 초기화
        </Button>
      </div>
    );
  }

  return (
    <div className="text-center py-12">
      <div className="mb-4">
        <Plus className="w-16 h-16 text-gray-300 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          첫 번째 프로젝트를 만들어보세요
        </h3>
        <p className="text-gray-500 mb-6">
          영상 제작 프로젝트를 시작하고 팀원들과 협업해보세요.
        </p>
      </div>
      {onCreateProject && (
        <Button onClick={onCreateProject} className="flex items-center gap-2">
          <Plus className="w-4 h-4" />
          새 프로젝트 만들기
        </Button>
      )}
    </div>
  );
};

// ========================================
// 메인 컴포넌트
// ========================================

export const ProjectList: React.FC<ProjectListProps> = ({
  className,
  enableSelection: _enableSelection = true,
  onProjectEdit,
  onProjectDelete,
  onProjectDuplicate,
  onProjectCreate,
  emptyStateContent,
  headerActions,
}) => {
  // Store hooks
  const {
    viewMode,
    searchQuery,
    pagination,
    sortConfig,
    showProjectThumbnails,
    compactCardMode,
    setViewMode,
    setSearchQuery,
    setPage,
    addToRecentProjects,
  } = useProjectStore();

  const { activeFilters, hasActiveFilters, clearFilters } = useProjectFilters();
  const { selectedIds, selectedCount, selectAll, clearSelection } = useProjectSelection();

  // 쿼리 파라미터 구성
  const queryParams: ProjectQueryParams = React.useMemo(() => {
    const params: ProjectQueryParams = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ordering: `${sortConfig.direction === 'desc' ? '-' : ''}${sortConfig.key}` as any,
    };

    if (searchQuery) {
      params.search = searchQuery;
    }

    if (activeFilters.status && activeFilters.status.length > 0) {
      params.status = activeFilters.status[0]; // API는 하나의 상태만 지원한다고 가정
    }

    return params;
  }, [pagination, sortConfig, searchQuery, activeFilters]);

  // 프로젝트 데이터 조회
  const {
    data: projectsResponse,
    isLoading,
    isError,
    error,
    refetch,
    isRefetching,
  } = useQuery({
    queryKey: projectQueryKeys.list(queryParams),
    queryFn: () => projectService.getProjects(queryParams),
    staleTime: 1000 * 60 * 5, // 5분
    gcTime: 1000 * 60 * 30, // 30분
    retry: 2,
  });

  const projects = projectsResponse?.success ? projectsResponse.data?.results ?? [] : [];
  const totalCount = projectsResponse?.success ? projectsResponse.data?.count ?? 0 : 0;

  // 핸들러들
  const handleProjectNavigate = React.useCallback((project: Project) => {
    addToRecentProjects(project.id);
    // 라우터 네비게이션 로직은 부모 컴포넌트에서 처리
    window.location.href = `/projects/${project.id}`;
  }, [addToRecentProjects]);

  const handleBulkActions = React.useMemo(() => ({
    selectAll: () => selectAll(projects.map(p => p.id)),
    clearSelection,
    archiveSelected: () => {
      // 벌크 아카이브 로직
      console.log('Archive selected:', selectedIds);
    },
    deleteSelected: () => {
      // 벌크 삭제 로직
      console.log('Delete selected:', selectedIds);
    },
  }), [projects, selectedIds, selectAll, clearSelection]);

  // 로딩 상태
  if (isLoading && !isRefetching) {
    return (
      <div className={cn('flex items-center justify-center py-12', className)}>
        <div className="text-center">
          <Loader2 className="w-8 h-8 text-gray-400 animate-spin mx-auto mb-4" />
          <p className="text-gray-500">프로젝트를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  // 에러 상태
  if (isError) {
    return (
      <div className={cn('flex items-center justify-center py-12', className)}>
        <div className="text-center">
          <AlertCircle className="w-8 h-8 text-red-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            프로젝트를 불러올 수 없습니다
          </h3>
          <p className="text-gray-500 mb-4">
            {error instanceof Error ? error.message : '알 수 없는 오류가 발생했습니다.'}
          </p>
          <Button onClick={() => refetch()} variant="outline">
            다시 시도
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className={cn('space-y-6', className)}>
      {/* 헤더 */}
      <ProjectListHeader
        projectCount={totalCount}
        selectedCount={selectedCount}
        viewMode={viewMode}
        searchQuery={searchQuery}
        isSearching={isRefetching}
        onViewModeChange={setViewMode}
        onSearchChange={setSearchQuery}
        onCreateProject={onProjectCreate}
        onToggleFilters={() => {
          // 필터 패널 토글 로직
          console.log('Toggle filters');
        }}
        onRefresh={() => refetch()}
        onBulkActions={handleBulkActions}
      />

      {/* 커스텀 헤더 액션 */}
      {headerActions && (
        <div className="border-t border-gray-200 pt-4">
          {headerActions}
        </div>
      )}

      {/* 프로젝트 그리드/리스트 */}
      <div className="relative">
        {/* 새로고침 로딩 오버레이 */}
        <AnimatePresence>
          {isRefetching && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 bg-white/50 backdrop-blur-sm z-10 flex items-center justify-center"
            >
              <div className="bg-white rounded-lg shadow-lg p-4 flex items-center gap-3">
                <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
                <span className="text-sm text-gray-700">업데이트 중...</span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* 빈 상태 */}
        {projects.length === 0 ? (
          <EmptyState
            hasFilters={hasActiveFilters}
            onCreateProject={onProjectCreate}
            onClearFilters={clearFilters}
            customContent={emptyStateContent}
          />
        ) : (
          <ProjectGrid
            projects={projects}
            viewMode={viewMode}
            showThumbnails={showProjectThumbnails}
            compactMode={compactCardMode}
            onProjectEdit={onProjectEdit}
            onProjectDelete={onProjectDelete}
            onProjectDuplicate={onProjectDuplicate}
            onProjectNavigate={handleProjectNavigate}
          />
        )}
      </div>

      {/* 페이지네이션 */}
      {projects.length > 0 && totalCount > pagination.pageSize && (
        <div className="flex justify-center mt-8">
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              onClick={() => setPage(pagination.page - 1)}
              disabled={pagination.page === 1}
            >
              이전
            </Button>
            
            <span className="px-4 py-2 text-sm text-gray-600">
              {pagination.page} / {Math.ceil(totalCount / pagination.pageSize)}
            </span>
            
            <Button
              variant="outline"
              onClick={() => setPage(pagination.page + 1)}
              disabled={pagination.page >= Math.ceil(totalCount / pagination.pageSize)}
            >
              다음
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};