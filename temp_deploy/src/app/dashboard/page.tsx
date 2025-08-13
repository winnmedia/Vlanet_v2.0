'use client';

import React, { Suspense } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Spinner } from '@/components/ui/Spinner';
import { 
  FolderOpen, 
  Calendar, 
  MessageSquare, 
  TrendingUp,
  Clock,
  Users,
  Film,
  CheckCircle2
} from 'lucide-react';
import Link from 'next/link';
import { cn } from '@/lib/cn';

// 대시보드 컴포넌트들을 lazy loading으로 분리
const DashboardStats = React.lazy(() => import('./components/DashboardStats'));
const RecentProjects = React.lazy(() => import('./components/RecentProjects'));
const QuickActions = React.lazy(() => import('./components/QuickActions'));
const ActivityTimeline = React.lazy(() => import('./components/ActivityTimeline'));

// 로딩 스피너 컴포넌트
const LoadingSpinner: React.FC = () => (
  <div className="flex items-center justify-center py-8">
    <Spinner size="lg" />
    <span className="ml-2 text-gray-600">로딩 중...</span>
  </div>
);

// 섹션별 로딩 스피너
const SectionLoader: React.FC<{ height?: string }> = ({ height = "h-32" }) => (
  <div className={cn("bg-white rounded-lg border border-gray-200 animate-pulse", height)}>
    <div className="p-6 space-y-4">
      <div className="h-4 bg-gray-200 rounded w-1/4"></div>
      <div className="space-y-2">
        <div className="h-3 bg-gray-200 rounded w-full"></div>
        <div className="h-3 bg-gray-200 rounded w-3/4"></div>
      </div>
    </div>
  </div>
);

interface RecentProjectProps {
  name: string;
  status: 'planning' | 'production' | 'feedback' | 'completed';
  updatedAt: string;
  progress: number;
}

export default function DashboardPage() {
  // 임시 데이터
  const stats = {
    totalProjects: 12,
    activeProjects: 8,
    completedTasks: 145,
    pendingFeedbacks: 23,
  };

  const recentProjects: RecentProjectProps[] = [
    {
      name: '브랜드 홍보 영상',
      status: 'production',
      updatedAt: '2시간 전',
      progress: 65,
    },
    {
      name: '제품 소개 애니메이션',
      status: 'feedback',
      updatedAt: '5시간 전',
      progress: 85,
    },
    {
      name: '유튜브 채널 인트로',
      status: 'planning',
      updatedAt: '1일 전',
      progress: 30,
    },
    {
      name: '소셜미디어 광고',
      status: 'completed',
      updatedAt: '2일 전',
      progress: 100,
    },
  ];

  return (
    <DashboardLayout>
      <div className="p-8">
        {/* 페이지 헤더 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">대시보드</h1>
          <p className="text-gray-600 mt-2">프로젝트 현황을 한눈에 확인하세요</p>
        </div>

        {/* 통계 카드 */}
        <Suspense 
          fallback={
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              {[...Array(4)].map((_, i) => (
                <SectionLoader key={i} height="h-24" />
              ))}
            </div>
          }
        >
          <DashboardStats stats={stats} />
        </Suspense>

        {/* 컨텐츠 그리드 */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 최근 프로젝트 */}
          <Suspense 
            fallback={<SectionLoader height="h-96" />}
          >
            <RecentProjects projects={recentProjects} />
          </Suspense>

          {/* 빠른 작업 */}
          <Suspense 
            fallback={<SectionLoader height="h-80" />}
          >
            <QuickActions />
          </Suspense>
        </div>

        {/* 활동 타임라인 */}
        <Suspense 
          fallback={<SectionLoader height="h-64" />}
        >
          <ActivityTimeline />
        </Suspense>
      </div>
    </DashboardLayout>
  );
}