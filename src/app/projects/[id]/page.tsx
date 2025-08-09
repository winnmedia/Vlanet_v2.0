'use client';

import React from 'react';
import { useQuery, QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useParams, useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import {
  ArrowLeft,
  Calendar,
  Users,
  Edit3,
  Share2,
  MoreVertical,
  Settings,
  Star,
  Clock,
  CheckCircle,
  Play,
  Loader2,
  AlertCircle,
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/cn';
import { projectService, projectQueryKeys } from '@/lib/api/project.service';
import { useProjectStore } from '@/store/project.store';
import type { Project, ProjectStatus } from '@/types';
import { format } from 'date-fns';
import { ko } from 'date-fns/locale';
import { Toaster } from 'sonner';

// QueryClient 인스턴스
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,
      gcTime: 1000 * 60 * 30,
      retry: 2,
    },
  },
});

// ========================================
// 상태별 스타일 설정
// ========================================

const statusConfig: Record<ProjectStatus, { 
  label: string; 
  color: string; 
  bgColor: string;
  icon: React.ComponentType<any>;
}> = {
  planning: {
    label: '기획 중',
    color: 'text-blue-600',
    bgColor: 'bg-blue-50 border-blue-200',
    icon: Edit3,
  },
  production: {
    label: '제작 중',
    color: 'text-orange-600',
    bgColor: 'bg-orange-50 border-orange-200',
    icon: Play,
  },
  review: {
    label: '검토 중',
    color: 'text-purple-600',
    bgColor: 'bg-purple-50 border-purple-200',
    icon: Clock,
  },
  completed: {
    label: '완료',
    color: 'text-green-600',
    bgColor: 'bg-green-50 border-green-200',
    icon: CheckCircle,
  },
  archived: {
    label: '보관됨',
    color: 'text-gray-500',
    bgColor: 'bg-gray-50 border-gray-200',
    icon: Settings,
  },
};

// ========================================
// 하위 컴포넌트들
// ========================================

interface ProjectHeaderProps {
  project: Project;
  onEdit: () => void;
  onShare: () => void;
}

const ProjectHeader: React.FC<ProjectHeaderProps> = ({
  project,
  onEdit,
  onShare,
}) => {
  const router = useRouter();
  const { addToRecentProjects } = useProjectStore();
  const statusInfo = statusConfig[project.status];
  const StatusIcon = statusInfo.icon;

  React.useEffect(() => {
    addToRecentProjects(project.id);
  }, [project.id, addToRecentProjects]);

  return (
    <div className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* 뒤로 가기 버튼 */}
        <div className="mb-6">
          <Button
            variant="ghost"
            onClick={() => router.back()}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="w-4 h-4" />
            프로젝트 목록으로
          </Button>
        </div>

        {/* 프로젝트 정보 */}
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3 mb-3">
              <h1 className="text-2xl font-bold text-gray-900 line-clamp-2">
                {project.title}
              </h1>
              
              <div className={cn(
                'inline-flex items-center gap-1 px-3 py-1 rounded-full border text-sm font-medium',
                statusInfo.bgColor,
                statusInfo.color
              )}>
                <StatusIcon className="w-4 h-4" />
                {statusInfo.label}
              </div>

              <button className="p-1 rounded-full hover:bg-gray-100 transition-colors">
                <Star className="w-5 h-5 text-gray-400 hover:text-yellow-500" />
              </button>
            </div>

            <p className="text-gray-600 mb-4 max-w-3xl">
              {project.description}
            </p>

            {/* 프로젝트 메타 정보 */}
            <div className="flex items-center gap-6 text-sm text-gray-500">
              <div className="flex items-center gap-1">
                <Calendar className="w-4 h-4" />
                <span>
                  {format(new Date(project.start_date), 'yyyy/MM/dd', { locale: ko })} ~ 
                  {format(new Date(project.end_date), 'yyyy/MM/dd', { locale: ko })}
                </span>
              </div>
              
              <div className="flex items-center gap-1">
                <Users className="w-4 h-4" />
                <span>{project.members_count || 0}명</span>
              </div>
              
              <div className="flex items-center gap-1">
                <span>소유자: {project.owner.nickname}</span>
              </div>
            </div>
          </div>

          {/* 액션 버튼들 */}
          <div className="flex items-center gap-2 ml-4">
            <Button
              variant="outline"
              onClick={onShare}
              className="flex items-center gap-2"
            >
              <Share2 className="w-4 h-4" />
              공유
            </Button>
            
            <Button
              onClick={onEdit}
              className="flex items-center gap-2"
            >
              <Edit3 className="w-4 h-4" />
              수정
            </Button>

            <Button variant="ghost" size="icon">
              <MoreVertical className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* 진행률 (있다면) */}
        {project.progress !== undefined && (
          <div className="mt-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">프로젝트 진행률</span>
              <span className="text-sm font-semibold text-gray-900">{project.progress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${project.progress}%` }}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

interface ProjectContentProps {
  project: Project;
}

const ProjectContent: React.FC<ProjectContentProps> = ({ project }) => {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* 메인 콘텐츠 영역 */}
        <div className="lg:col-span-2 space-y-8">
          {/* 프로젝트 상세 정보 */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">프로젝트 상세</h2>
            <div className="prose max-w-none">
              <p className="text-gray-700 leading-relaxed">
                {project.description}
              </p>
            </div>
          </div>

          {/* 파일 목록 */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">프로젝트 파일</h2>
            <div className="text-center py-12">
              <div className="text-gray-400 mb-4">
                <svg className="w-16 h-16 mx-auto" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
                </svg>
              </div>
              <h3 className="text-sm font-medium text-gray-900 mb-1">파일이 없습니다</h3>
              <p className="text-sm text-gray-500 mb-4">
                첫 번째 파일을 업로드해보세요.
              </p>
              <Button size="sm">
                파일 업로드
              </Button>
            </div>
          </div>

          {/* 활동 내역 */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">최근 활동</h2>
            <div className="text-center py-12">
              <div className="text-gray-400 mb-4">
                <Clock className="w-16 h-16 mx-auto" />
              </div>
              <h3 className="text-sm font-medium text-gray-900 mb-1">활동 내역이 없습니다</h3>
              <p className="text-sm text-gray-500">
                프로젝트 활동이 시작되면 여기에 표시됩니다.
              </p>
            </div>
          </div>
        </div>

        {/* 사이드바 */}
        <div className="space-y-6">
          {/* 프로젝트 정보 */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">프로젝트 정보</h3>
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-500">상태</label>
                <div className="mt-1">
                  <div className={cn(
                    'inline-flex items-center gap-1 px-2 py-1 rounded-full border text-xs font-medium',
                    statusConfig[project.status].bgColor,
                    statusConfig[project.status].color
                  )}>
                    {React.createElement(statusConfig[project.status].icon, { className: 'w-3 h-3' })}
                    {statusConfig[project.status].label}
                  </div>
                </div>
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-500">시작일</label>
                <p className="mt-1 text-sm text-gray-900">
                  {format(new Date(project.start_date), 'yyyy년 MM월 dd일', { locale: ko })}
                </p>
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-500">종료일</label>
                <p className="mt-1 text-sm text-gray-900">
                  {format(new Date(project.end_date), 'yyyy년 MM월 dd일', { locale: ko })}
                </p>
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-500">공개 설정</label>
                <p className="mt-1 text-sm text-gray-900">
                  {project.is_public ? '공개' : '비공개'}
                </p>
              </div>
            </div>
          </div>

          {/* 팀원 목록 */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">팀원</h3>
              <Button size="sm" variant="outline">
                초대
              </Button>
            </div>
            
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-xs font-medium">
                    {project.owner.nickname.charAt(0).toUpperCase()}
                  </span>
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">
                    {project.owner.nickname}
                  </p>
                  <p className="text-xs text-gray-500">소유자</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// ========================================
// 메인 프로젝트 상세 페이지 컴포넌트
// ========================================

const ProjectDetailPageContent: React.FC = () => {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id ? Number(params.id) : null;

  // 프로젝트 상세 정보 조회
  const {
    data: projectResponse,
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: projectQueryKeys.detail(projectId!),
    queryFn: () => projectService.getProjectDetail(projectId!),
    enabled: !!projectId,
  });

  const project = projectResponse?.success ? projectResponse.data : null;

  // 수정 핸들러
  const handleEdit = () => {
    router.push(`/projects/${projectId}/edit`);
  };

  // 공유 핸들러
  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: project?.title,
        text: project?.description,
        url: window.location.href,
      });
    } else {
      // 폴백: 클립보드에 복사
      navigator.clipboard.writeText(window.location.href);
      // 토스트 메시지 표시 로직
    }
  };

  // 로딩 상태
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 text-gray-400 animate-spin mx-auto mb-4" />
          <p className="text-gray-500">프로젝트를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  // 에러 상태
  if (isError || !project) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-8 h-8 text-red-400 mx-auto mb-4" />
          <h1 className="text-xl font-semibold text-gray-900 mb-2">
            프로젝트를 찾을 수 없습니다
          </h1>
          <p className="text-gray-500 mb-4">
            {error instanceof Error ? error.message : '프로젝트가 존재하지 않거나 접근 권한이 없습니다.'}
          </p>
          <Button onClick={() => router.push('/projects')} variant="outline">
            프로젝트 목록으로
          </Button>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="min-h-screen bg-gray-50"
    >
      {/* 프로젝트 헤더 */}
      <ProjectHeader
        project={project}
        onEdit={handleEdit}
        onShare={handleShare}
      />

      {/* 프로젝트 내용 */}
      <ProjectContent project={project} />

      {/* 토스트 알림 */}
      <Toaster position="top-right" />
    </motion.div>
  );
};

// ========================================
// 메인 페이지 컴포넌트
// ========================================

export default function ProjectDetailPage() {
  return (
    <QueryClientProvider client={queryClient}>
      <ProjectDetailPageContent />
    </QueryClientProvider>
  );
}