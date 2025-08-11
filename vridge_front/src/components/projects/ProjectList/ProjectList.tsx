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
//  
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
//  
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

  //  
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
      {/*   */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h1 className="text-2xl font-bold text-gray-900">
             
            <span className="ml-2 text-sm font-normal text-gray-500">
              ({projectCount.toLocaleString()})
            </span>
          </h1>
          
          {selectedCount > 0 && (
            <div className="flex items-center gap-2 px-3 py-1 bg-blue-50 border border-blue-200 rounded-lg">
              <span className="text-sm text-blue-700 font-medium">
                {selectedCount} 
              </span>
              <div className="flex items-center gap-1">
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={onBulkActions.archiveSelected}
                  className="h-6 px-2 text-xs"
                >
                  <Archive className="w-3 h-3 mr-1" />
                  
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={onBulkActions.deleteSelected}
                  className="h-6 px-2 text-xs text-red-600 hover:text-red-700 hover:bg-red-50"
                >
                  <Trash2 className="w-3 h-3 mr-1" />
                  
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={onBulkActions.clearSelection}
                  className="h-6 px-2 text-xs"
                >
                   
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
               
            </Button>
          )}
        </div>
      </div>

      {/*     */}
      <div className="flex items-center gap-3">
        {/*  */}
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <Input
            type="text"
            placeholder=" ..."
            value={localSearch}
            onChange={(e) => setLocalSearch(e.target.value)}
            className="pl-10"
          />
          {isSearching && (
            <Loader2 className="absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 animate-spin" />
          )}
        </div>

        {/*   */}
        <Button
          variant="outline"
          onClick={onToggleFilters}
          className="flex items-center gap-2"
        >
          <Filter className="w-4 h-4" />
          
        </Button>

        {/*   */}
        <Button
          variant="outline"
          className="flex items-center gap-2"
        >
          <ArrowUpDown className="w-4 h-4" />
          
        </Button>

        {/*    */}
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

        {/*   */}
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
  //  variants
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
              
          </h3>
          <p className="text-gray-500 mb-6">
               .
          </p>
        </div>
        <Button onClick={onClearFilters} variant="outline">
           
        </Button>
      </div>
    );
  }

  return (
    <div className="text-center py-12">
      <div className="mb-4">
        <Plus className="w-16 h-16 text-gray-300 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">
             
        </h3>
        <p className="text-gray-500 mb-6">
               .
        </p>
      </div>
      {onCreateProject && (
        <Button onClick={onCreateProject} className="flex items-center gap-2">
          <Plus className="w-4 h-4" />
            
        </Button>
      )}
    </div>
  );
};

// ========================================
//  
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

  //   
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
      params.status = activeFilters.status[0]; // API    
    }

    return params;
  }, [pagination, sortConfig, searchQuery, activeFilters]);

  //   
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
    staleTime: 1000 * 60 * 5, // 5
    gcTime: 1000 * 60 * 30, // 30
    retry: 2,
  });

  const projects = projectsResponse?.success ? projectsResponse.data?.results ?? [] : [];
  const totalCount = projectsResponse?.success ? projectsResponse.data?.count ?? 0 : 0;

  // 
  const handleProjectNavigate = React.useCallback((project: Project) => {
    addToRecentProjects(project.id);
    //      
    window.location.href = `/projects/${project.id}`;
  }, [addToRecentProjects]);

  const handleBulkActions = React.useMemo(() => ({
    selectAll: () => selectAll(projects.map(p => p.id)),
    clearSelection,
    archiveSelected: () => {
      //   
      console.log('Archive selected:', selectedIds);
    },
    deleteSelected: () => {
      //   
      console.log('Delete selected:', selectedIds);
    },
  }), [projects, selectedIds, selectAll, clearSelection]);

  //  
  if (isLoading && !isRefetching) {
    return (
      <div className={cn('flex items-center justify-center py-12', className)}>
        <div className="text-center">
          <Loader2 className="w-8 h-8 text-gray-400 animate-spin mx-auto mb-4" />
          <p className="text-gray-500">  ...</p>
        </div>
      </div>
    );
  }

  //  
  if (isError) {
    return (
      <div className={cn('flex items-center justify-center py-12', className)}>
        <div className="text-center">
          <AlertCircle className="w-8 h-8 text-red-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
               
          </h3>
          <p className="text-gray-500 mb-4">
            {error instanceof Error ? error.message : '    .'}
          </p>
          <Button onClick={() => refetch()} variant="outline">
             
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className={cn('space-y-6', className)}>
      {/*  */}
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
          //    
          console.log('Toggle filters');
        }}
        onRefresh={() => refetch()}
        onBulkActions={handleBulkActions}
      />

      {/*    */}
      {headerActions && (
        <div className="border-t border-gray-200 pt-4">
          {headerActions}
        </div>
      )}

      {/*  / */}
      <div className="relative">
        {/*    */}
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
                <span className="text-sm text-gray-700"> ...</span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/*   */}
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

      {/*  */}
      {projects.length > 0 && totalCount > pagination.pageSize && (
        <div className="flex justify-center mt-8">
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              onClick={() => setPage(pagination.page - 1)}
              disabled={pagination.page === 1}
            >
              
            </Button>
            
            <span className="px-4 py-2 text-sm text-gray-600">
              {pagination.page} / {Math.ceil(totalCount / pagination.pageSize)}
            </span>
            
            <Button
              variant="outline"
              onClick={() => setPage(pagination.page + 1)}
              disabled={pagination.page >= Math.ceil(totalCount / pagination.pageSize)}
            >
              
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};