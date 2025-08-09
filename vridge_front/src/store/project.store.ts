import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import type { 
  ProjectFilters, 
  PaginationState,
  SortConfig,
} from '@/types';

// ========================================
// 상태 인터페이스 (Client State Only)
// 서버 상태는 TanStack Query가 관리
// ========================================

interface ProjectUIState {
  // 뷰 모드 (Grid/List)
  viewMode: 'grid' | 'list';
  
  // 필터링 상태
  activeFilters: ProjectFilters;
  filtersPanelOpen: boolean;
  
  // 정렬 설정
  sortConfig: SortConfig;
  
  // 페이지네이션 (클라이언트 상태)
  pagination: PaginationState;
  
  // 선택된 프로젝트들 (다중 선택용)
  selectedProjectIds: number[];
  
  // 모달 상태
  createModalOpen: boolean;
  editModalOpen: boolean;
  deleteModalOpen: boolean;
  duplicateModalOpen: boolean;
  editingProjectId: number | null;
  
  // 검색 상태
  searchQuery: string;
  searchSuggestions: string[];
  searchHistoryVisible: boolean;
  
  // 사이드바 및 레이아웃
  sidebarCollapsed: boolean;
  
  // 프로젝트 카드 설정
  showProjectThumbnails: boolean;
  compactCardMode: boolean;
  
  // 즐겨찾기 필터
  showFavoritesOnly: boolean;
  
  // 최근 열어본 프로젝트
  recentProjectIds: number[];
  
  // 드래그 앤 드롭 상태
  draggedProjectId: number | null;
  
  // 로딩 상태 (UI 관련만)
  isFiltersLoading: boolean;
  isSearching: boolean;
}

interface ProjectUIActions {
  // 뷰 모드 관리
  setViewMode: (mode: 'grid' | 'list') => void;
  toggleViewMode: () => void;
  
  // 필터링 액션
  updateFilters: (filters: Partial<ProjectFilters>) => void;
  clearFilters: () => void;
  toggleFiltersPanel: () => void;
  setFiltersPanelOpen: (open: boolean) => void;
  
  // 정렬 액션
  updateSort: (config: SortConfig) => void;
  toggleSortDirection: (key: string) => void;
  
  // 페이지네이션 액션
  setPage: (page: number) => void;
  setPageSize: (pageSize: number) => void;
  resetPagination: () => void;
  
  // 선택 관리
  selectProject: (id: number) => void;
  selectProjects: (ids: number[]) => void;
  deselectProject: (id: number) => void;
  toggleProjectSelection: (id: number) => void;
  clearSelection: () => void;
  selectAll: (projectIds: number[]) => void;
  
  // 모달 관리
  openCreateModal: () => void;
  openEditModal: (projectId: number) => void;
  openDeleteModal: (projectId: number) => void;
  openDuplicateModal: (projectId: number) => void;
  closeAllModals: () => void;
  
  // 검색 관리
  setSearchQuery: (query: string) => void;
  clearSearch: () => void;
  addSearchSuggestion: (suggestion: string) => void;
  clearSearchSuggestions: () => void;
  toggleSearchHistory: () => void;
  
  // 레이아웃 관리
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  
  // 프로젝트 카드 설정
  toggleProjectThumbnails: () => void;
  toggleCompactMode: () => void;
  
  // 즐겨찾기
  toggleFavoritesFilter: () => void;
  
  // 최근 열어본 프로젝트 관리
  addToRecentProjects: (projectId: number) => void;
  removeFromRecentProjects: (projectId: number) => void;
  clearRecentProjects: () => void;
  
  // 드래그 앤 드롭
  setDraggedProject: (projectId: number | null) => void;
  
  // 상태 초기화
  resetUI: () => void;
  resetFilters: () => void;
  resetModals: () => void;
}

type ProjectStore = ProjectUIState & ProjectUIActions;

// ========================================
// 초기 상태
// ========================================

const initialState: ProjectUIState = {
  // 뷰 설정
  viewMode: 'grid',
  
  // 필터링
  activeFilters: {},
  filtersPanelOpen: false,
  
  // 정렬
  sortConfig: {
    key: 'updated_at',
    direction: 'desc',
  },
  
  // 페이지네이션
  pagination: {
    page: 1,
    pageSize: 12,
    total: 0,
  },
  
  // 선택
  selectedProjectIds: [],
  
  // 모달
  createModalOpen: false,
  editModalOpen: false,
  deleteModalOpen: false,
  duplicateModalOpen: false,
  editingProjectId: null,
  
  // 검색
  searchQuery: '',
  searchSuggestions: [],
  searchHistoryVisible: false,
  
  // 레이아웃
  sidebarCollapsed: false,
  
  // 카드 설정
  showProjectThumbnails: true,
  compactCardMode: false,
  
  // 필터
  showFavoritesOnly: false,
  
  // 최근 프로젝트
  recentProjectIds: [],
  
  // 드래그 앤 드롭
  draggedProjectId: null,
  
  // 로딩 상태
  isFiltersLoading: false,
  isSearching: false,
};

// ========================================
// 유틸리티 함수
// ========================================

/**
 * 필터가 활성 상태인지 확인
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
 * 최근 프로젝트 목록을 최대 10개로 제한하고 중복 제거
 */
const updateRecentProjects = (current: number[], newId: number): number[] => {
  const filtered = current.filter(id => id !== newId);
  const updated = [newId, ...filtered];
  return updated.slice(0, 10);
};

// ========================================
// Zustand Store 생성 
// ========================================

export const useProjectStore = create<ProjectStore>()(
  subscribeWithSelector(
    (set, get) => ({
      ...initialState,

      // ========================================
      // 뷰 모드 관리
      // ========================================

      setViewMode: (mode) => {
        set({ viewMode: mode });
        // 뷰 모드가 변경되면 선택 해제
        set({ selectedProjectIds: [] });
      },

      toggleViewMode: () => {
        const current = get().viewMode;
        set({ viewMode: current === 'grid' ? 'list' : 'grid' });
        set({ selectedProjectIds: [] });
      },

      // ========================================
      // 필터링 관리
      // ========================================

      updateFilters: (filters) => {
        const currentFilters = get().activeFilters;
        const newFilters = { ...currentFilters, ...filters };
        
        set({ 
          activeFilters: newFilters,
          // 필터 변경 시 페이지네이션 리셋
          pagination: { ...get().pagination, page: 1 },
          // 선택 해제
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
      // 정렬 관리
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
      // 페이지네이션 관리
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
      // 선택 관리
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
      // 모달 관리
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
      // 검색 관리
      // ========================================

      setSearchQuery: (query) => {
        set({ 
          searchQuery: query,
          // 검색어 변경 시 페이지네이션 리셋
          pagination: { ...get().pagination, page: 1 },
          selectedProjectIds: [],
        });
        
        // 필터에도 검색어 반영
        get().updateFilters({ search: query });
      },

      clearSearch: () => {
        set({ 
          searchQuery: '',
          pagination: { ...get().pagination, page: 1 },
          selectedProjectIds: [],
        });
        
        // 필터에서도 검색어 제거
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
      // 레이아웃 관리
      // ========================================

      toggleSidebar: () => {
        set({ sidebarCollapsed: !get().sidebarCollapsed });
      },

      setSidebarCollapsed: (collapsed) => {
        set({ sidebarCollapsed: collapsed });
      },

      // ========================================
      // 프로젝트 카드 설정
      // ========================================

      toggleProjectThumbnails: () => {
        set({ showProjectThumbnails: !get().showProjectThumbnails });
      },

      toggleCompactMode: () => {
        set({ compactCardMode: !get().compactCardMode });
      },

      // ========================================
      // 즐겨찾기 관리
      // ========================================

      toggleFavoritesFilter: () => {
        set({ showFavoritesOnly: !get().showFavoritesOnly });
      },

      // ========================================
      // 최근 열어본 프로젝트 관리
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
      // 드래그 앤 드롭
      // ========================================

      setDraggedProject: (projectId) => {
        set({ draggedProjectId: projectId });
      },

      // ========================================
      // 상태 초기화
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
// 선택자 (Selectors)
// ========================================

// 계산된 값들을 위한 선택자들
export const projectSelectors = {
  // 활성 필터가 있는지 확인
  hasActiveFilters: (state: ProjectUIState) => hasActiveFilters(state.activeFilters),
  
  // 선택된 프로젝트 개수
  selectedCount: (state: ProjectUIState) => state.selectedProjectIds.length,
  
  // 특정 프로젝트가 선택되어 있는지 확인
  isProjectSelected: (state: ProjectUIState, projectId: number) => 
    state.selectedProjectIds.includes(projectId),
    
  // 모달이 열려 있는지 확인
  hasOpenModal: (state: ProjectUIState) => 
    state.createModalOpen || state.editModalOpen || state.deleteModalOpen || state.duplicateModalOpen,
    
  // 현재 편집 중인 프로젝트가 있는지 확인
  isEditing: (state: ProjectUIState) => state.editingProjectId !== null,
  
  // 검색 중인지 확인
  isSearchActive: (state: ProjectUIState) => Boolean(state.searchQuery.trim()),
  
  // 필터 패널이 필요한지 확인 (필터가 많거나 활성 상태일 때)
  shouldShowFiltersPanel: (state: ProjectUIState) => 
    state.filtersPanelOpen || hasActiveFilters(state.activeFilters),
};

// ========================================
// 훅 형태의 편의 함수들
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
// 로컬 스토리지 동기화
// ========================================

// 특정 UI 상태는 로컬 스토리지에 저장하여 세션 간 유지
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
  
  // 초기화 시 로컬 스토리지에서 불러오기
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