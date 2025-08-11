import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import type { 
  ProjectFilters, 
  PaginationState,
  SortConfig,
} from '@/types';

// ========================================
//   (Client State Only)
//   TanStack Query 
// ========================================

interface ProjectUIState {
  //   (Grid/List)
  viewMode: 'grid' | 'list';
  
  //  
  activeFilters: ProjectFilters;
  filtersPanelOpen: boolean;
  
  //  
  sortConfig: SortConfig;
  
  //  ( )
  pagination: PaginationState;
  
  //   ( )
  selectedProjectIds: number[];
  
  //  
  createModalOpen: boolean;
  editModalOpen: boolean;
  deleteModalOpen: boolean;
  duplicateModalOpen: boolean;
  editingProjectId: number | null;
  
  //  
  searchQuery: string;
  searchSuggestions: string[];
  searchHistoryVisible: boolean;
  
  //   
  sidebarCollapsed: boolean;
  
  //   
  showProjectThumbnails: boolean;
  compactCardMode: boolean;
  
  //  
  showFavoritesOnly: boolean;
  
  //   
  recentProjectIds: number[];
  
  //    
  draggedProjectId: number | null;
  
  //   (UI )
  isFiltersLoading: boolean;
  isSearching: boolean;
}

interface ProjectUIActions {
  //   
  setViewMode: (mode: 'grid' | 'list') => void;
  toggleViewMode: () => void;
  
  //  
  updateFilters: (filters: Partial<ProjectFilters>) => void;
  clearFilters: () => void;
  toggleFiltersPanel: () => void;
  setFiltersPanelOpen: (open: boolean) => void;
  
  //  
  updateSort: (config: SortConfig) => void;
  toggleSortDirection: (key: string) => void;
  
  //  
  setPage: (page: number) => void;
  setPageSize: (pageSize: number) => void;
  resetPagination: () => void;
  
  //  
  selectProject: (id: number) => void;
  selectProjects: (ids: number[]) => void;
  deselectProject: (id: number) => void;
  toggleProjectSelection: (id: number) => void;
  clearSelection: () => void;
  selectAll: (projectIds: number[]) => void;
  
  //  
  openCreateModal: () => void;
  openEditModal: (projectId: number) => void;
  openDeleteModal: (projectId: number) => void;
  openDuplicateModal: (projectId: number) => void;
  closeAllModals: () => void;
  
  //  
  setSearchQuery: (query: string) => void;
  clearSearch: () => void;
  addSearchSuggestion: (suggestion: string) => void;
  clearSearchSuggestions: () => void;
  toggleSearchHistory: () => void;
  
  //  
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  
  //   
  toggleProjectThumbnails: () => void;
  toggleCompactMode: () => void;
  
  // 
  toggleFavoritesFilter: () => void;
  
  //    
  addToRecentProjects: (projectId: number) => void;
  removeFromRecentProjects: (projectId: number) => void;
  clearRecentProjects: () => void;
  
  //   
  setDraggedProject: (projectId: number | null) => void;
  
  //  
  resetUI: () => void;
  resetFilters: () => void;
  resetModals: () => void;
}

type ProjectStore = ProjectUIState & ProjectUIActions;

// ========================================
//  
// ========================================

const initialState: ProjectUIState = {
  //  
  viewMode: 'grid',
  
  // 
  activeFilters: {},
  filtersPanelOpen: false,
  
  // 
  sortConfig: {
    key: 'updated_at',
    direction: 'desc',
  },
  
  // 
  pagination: {
    page: 1,
    pageSize: 12,
    total: 0,
  },
  
  // 
  selectedProjectIds: [],
  
  // 
  createModalOpen: false,
  editModalOpen: false,
  deleteModalOpen: false,
  duplicateModalOpen: false,
  editingProjectId: null,
  
  // 
  searchQuery: '',
  searchSuggestions: [],
  searchHistoryVisible: false,
  
  // 
  sidebarCollapsed: false,
  
  //  
  showProjectThumbnails: true,
  compactCardMode: false,
  
  // 
  showFavoritesOnly: false,
  
  //  
  recentProjectIds: [],
  
  //   
  draggedProjectId: null,
  
  //  
  isFiltersLoading: false,
  isSearching: false,
};

// ========================================
//  
// ========================================

/**
 *    
 */
const hasActiveFilters = (filters: ProjectFilters): boolean => {
  return Boolean(
    filters.search ||
    (filters.status && filters.status.length > 0) ||
    (filters.owner && filters.owner.length > 0) ||
    filters.dateRange ||
    (filters.tags && filters.tags.length > 0)
  );
};

/**
 *     10   
 */
const updateRecentProjects = (current: number[], newId: number): number[] => {
  const filtered = current.filter(id => id !== newId);
  const updated = [newId, ...filtered];
  return updated.slice(0, 10);
};

// ========================================
// Zustand Store  
// ========================================

export const useProjectStore = create<ProjectStore>()(
  subscribeWithSelector(
    (set, get) => ({
      ...initialState,

      // ========================================
      //   
      // ========================================

      setViewMode: (mode) => {
        set({ viewMode: mode });
        //     
        set({ selectedProjectIds: [] });
      },

      toggleViewMode: () => {
        const current = get().viewMode;
        set({ viewMode: current === 'grid' ? 'list' : 'grid' });
        set({ selectedProjectIds: [] });
      },

      // ========================================
      //  
      // ========================================

      updateFilters: (filters) => {
        const currentFilters = get().activeFilters;
        const newFilters = { ...currentFilters, ...filters };
        
        set({ 
          activeFilters: newFilters,
          //     
          pagination: { ...get().pagination, page: 1 },
          //  
          selectedProjectIds: [],
        });
      },

      clearFilters: () => {
        set({ 
          activeFilters: {},
          pagination: { ...get().pagination, page: 1 },
          selectedProjectIds: [],
          showFavoritesOnly: false,
        });
      },

      toggleFiltersPanel: () => {
        set({ filtersPanelOpen: !get().filtersPanelOpen });
      },

      setFiltersPanelOpen: (open) => {
        set({ filtersPanelOpen: open });
      },

      // ========================================
      //  
      // ========================================

      updateSort: (config) => {
        set({ 
          sortConfig: config,
          pagination: { ...get().pagination, page: 1 },
          selectedProjectIds: [],
        });
      },

      toggleSortDirection: (key) => {
        const current = get().sortConfig;
        const newDirection = current.key === key && current.direction === 'asc' ? 'desc' : 'asc';
        
        set({ 
          sortConfig: { key, direction: newDirection },
          pagination: { ...get().pagination, page: 1 },
          selectedProjectIds: [],
        });
      },

      // ========================================
      //  
      // ========================================

      setPage: (page) => {
        set({ 
          pagination: { ...get().pagination, page },
          selectedProjectIds: [],
        });
      },

      setPageSize: (pageSize) => {
        set({ 
          pagination: { ...get().pagination, pageSize, page: 1 },
          selectedProjectIds: [],
        });
      },

      resetPagination: () => {
        set({ 
          pagination: { ...get().pagination, page: 1, total: 0 },
        });
      },

      // ========================================
      //  
      // ========================================

      selectProject: (id) => {
        const current = get().selectedProjectIds;
        if (!current.includes(id)) {
          set({ selectedProjectIds: [...current, id] });
        }
      },

      selectProjects: (ids) => {
        set({ selectedProjectIds: ids });
      },

      deselectProject: (id) => {
        const current = get().selectedProjectIds;
        set({ selectedProjectIds: current.filter(projectId => projectId !== id) });
      },

      toggleProjectSelection: (id) => {
        const current = get().selectedProjectIds;
        if (current.includes(id)) {
          set({ selectedProjectIds: current.filter(projectId => projectId !== id) });
        } else {
          set({ selectedProjectIds: [...current, id] });
        }
      },

      clearSelection: () => {
        set({ selectedProjectIds: [] });
      },

      selectAll: (projectIds) => {
        set({ selectedProjectIds: [...projectIds] });
      },

      // ========================================
      //  
      // ========================================

      openCreateModal: () => {
        set({ 
          createModalOpen: true,
          editModalOpen: false,
          deleteModalOpen: false,
          duplicateModalOpen: false,
          editingProjectId: null,
        });
      },

      openEditModal: (projectId) => {
        set({ 
          editModalOpen: true,
          createModalOpen: false,
          deleteModalOpen: false,
          duplicateModalOpen: false,
          editingProjectId: projectId,
        });
      },

      openDeleteModal: (projectId) => {
        set({ 
          deleteModalOpen: true,
          createModalOpen: false,
          editModalOpen: false,
          duplicateModalOpen: false,
          editingProjectId: projectId,
        });
      },

      openDuplicateModal: (projectId) => {
        set({ 
          duplicateModalOpen: true,
          createModalOpen: false,
          editModalOpen: false,
          deleteModalOpen: false,
          editingProjectId: projectId,
        });
      },

      closeAllModals: () => {
        set({ 
          createModalOpen: false,
          editModalOpen: false,
          deleteModalOpen: false,
          duplicateModalOpen: false,
          editingProjectId: null,
        });
      },

      // ========================================
      //  
      // ========================================

      setSearchQuery: (query) => {
        set({ 
          searchQuery: query,
          //     
          pagination: { ...get().pagination, page: 1 },
          selectedProjectIds: [],
        });
        
        //   
        get().updateFilters({ search: query });
      },

      clearSearch: () => {
        set({ 
          searchQuery: '',
          pagination: { ...get().pagination, page: 1 },
          selectedProjectIds: [],
        });
        
        //   
        const { search, ...otherFilters } = get().activeFilters;
        set({ activeFilters: otherFilters });
      },

      addSearchSuggestion: (suggestion) => {
        const current = get().searchSuggestions;
        if (!current.includes(suggestion)) {
          set({ searchSuggestions: [suggestion, ...current].slice(0, 5) });
        }
      },

      clearSearchSuggestions: () => {
        set({ searchSuggestions: [] });
      },

      toggleSearchHistory: () => {
        set({ searchHistoryVisible: !get().searchHistoryVisible });
      },

      // ========================================
      //  
      // ========================================

      toggleSidebar: () => {
        set({ sidebarCollapsed: !get().sidebarCollapsed });
      },

      setSidebarCollapsed: (collapsed) => {
        set({ sidebarCollapsed: collapsed });
      },

      // ========================================
      //   
      // ========================================

      toggleProjectThumbnails: () => {
        set({ showProjectThumbnails: !get().showProjectThumbnails });
      },

      toggleCompactMode: () => {
        set({ compactCardMode: !get().compactCardMode });
      },

      // ========================================
      //  
      // ========================================

      toggleFavoritesFilter: () => {
        set({ showFavoritesOnly: !get().showFavoritesOnly });
      },

      // ========================================
      //    
      // ========================================

      addToRecentProjects: (projectId) => {
        const current = get().recentProjectIds;
        const updated = updateRecentProjects(current, projectId);
        set({ recentProjectIds: updated });
      },

      removeFromRecentProjects: (projectId) => {
        const current = get().recentProjectIds;
        set({ recentProjectIds: current.filter(id => id !== projectId) });
      },

      clearRecentProjects: () => {
        set({ recentProjectIds: [] });
      },

      // ========================================
      //   
      // ========================================

      setDraggedProject: (projectId) => {
        set({ draggedProjectId: projectId });
      },

      // ========================================
      //  
      // ========================================

      resetUI: () => {
        set({ ...initialState });
      },

      resetFilters: () => {
        set({ 
          activeFilters: {},
          showFavoritesOnly: false,
          pagination: { ...get().pagination, page: 1 },
          selectedProjectIds: [],
        });
      },

      resetModals: () => {
        set({ 
          createModalOpen: false,
          editModalOpen: false,
          deleteModalOpen: false,
          duplicateModalOpen: false,
          editingProjectId: null,
        });
      },
    })
  )
);

// ========================================
//  (Selectors)
// ========================================

//    
export const projectSelectors = {
  //    
  hasActiveFilters: (state: ProjectUIState) => hasActiveFilters(state.activeFilters),
  
  //   
  selectedCount: (state: ProjectUIState) => state.selectedProjectIds.length,
  
  //     
  isProjectSelected: (state: ProjectUIState, projectId: number) => 
    state.selectedProjectIds.includes(projectId),
    
  //    
  hasOpenModal: (state: ProjectUIState) => 
    state.createModalOpen || state.editModalOpen || state.deleteModalOpen || state.duplicateModalOpen,
    
  //      
  isEditing: (state: ProjectUIState) => state.editingProjectId !== null,
  
  //   
  isSearchActive: (state: ProjectUIState) => Boolean(state.searchQuery.trim()),
  
  //     (    )
  shouldShowFiltersPanel: (state: ProjectUIState) => 
    state.filtersPanelOpen || hasActiveFilters(state.activeFilters),
};

// ========================================
//    
// ========================================

export const useProjectSelection = () => {
  const selectedIds = useProjectStore(state => state.selectedProjectIds);
  const selectProject = useProjectStore(state => state.selectProject);
  const deselectProject = useProjectStore(state => state.deselectProject);
  const toggleSelection = useProjectStore(state => state.toggleProjectSelection);
  const clearSelection = useProjectStore(state => state.clearSelection);
  const selectAll = useProjectStore(state => state.selectAll);
  
  return {
    selectedIds,
    selectedCount: selectedIds.length,
    isSelected: (id: number) => selectedIds.includes(id),
    selectProject,
    deselectProject,
    toggleSelection,
    clearSelection,
    selectAll,
  };
};

export const useProjectModals = () => {
  const {
    createModalOpen,
    editModalOpen,
    deleteModalOpen,
    duplicateModalOpen,
    editingProjectId,
    openCreateModal,
    openEditModal,
    openDeleteModal,
    openDuplicateModal,
    closeAllModals,
  } = useProjectStore();
  
  return {
    createModalOpen,
    editModalOpen,
    deleteModalOpen,
    duplicateModalOpen,
    editingProjectId,
    hasOpenModal: createModalOpen || editModalOpen || deleteModalOpen || duplicateModalOpen,
    openCreateModal,
    openEditModal,
    openDeleteModal,
    openDuplicateModal,
    closeAllModals,
  };
};

export const useProjectFilters = () => {
  const {
    activeFilters,
    updateFilters,
    clearFilters,
    resetFilters,
    showFavoritesOnly,
    toggleFavoritesFilter,
  } = useProjectStore();
  
  return {
    activeFilters,
    hasActiveFilters: hasActiveFilters(activeFilters),
    updateFilters,
    clearFilters,
    resetFilters,
    showFavoritesOnly,
    toggleFavoritesFilter,
  };
};

// ========================================
//   
// ========================================

//  UI       
export const syncUIPreferences = () => {
  useProjectStore.subscribe(
    (state) => ({
      viewMode: state.viewMode,
      sidebarCollapsed: state.sidebarCollapsed,
      showProjectThumbnails: state.showProjectThumbnails,
      compactCardMode: state.compactCardMode,
      sortConfig: state.sortConfig,
      pagination: { pageSize: state.pagination.pageSize },
    }),
    (preferences) => {
      if (typeof window !== 'undefined') {
        localStorage.setItem('videoplanet-project-preferences', JSON.stringify(preferences));
      }
    }
  );
  
  //     
  if (typeof window !== 'undefined') {
    try {
      const saved = localStorage.getItem('videoplanet-project-preferences');
      if (saved) {
        const preferences = JSON.parse(saved);
        useProjectStore.setState((state) => ({
          ...state,
          ...preferences,
          pagination: {
            ...state.pagination,
            pageSize: preferences.pagination?.pageSize || state.pagination.pageSize,
          },
        }));
      }
    } catch (error) {
      console.warn('Failed to load project preferences from localStorage:', error);
    }
  }
};