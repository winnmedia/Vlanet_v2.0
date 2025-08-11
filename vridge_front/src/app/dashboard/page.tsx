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

//   lazy loading 
const DashboardStats = React.lazy(() => import('./components/DashboardStats'));
const RecentProjects = React.lazy(() => import('./components/RecentProjects'));
const QuickActions = React.lazy(() => import('./components/QuickActions'));
const ActivityTimeline = React.lazy(() => import('./components/ActivityTimeline'));

//   
const LoadingSpinner: React.FC = () => (
  <div className="flex items-center justify-center py-8">
    <Spinner size="lg" />
    <span className="ml-2 text-gray-600"> ...</span>
  </div>
);

//   
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
  //  
  const stats = {
    totalProjects: 12,
    activeProjects: 8,
    completedTasks: 145,
    pendingFeedbacks: 23,
  };

  const recentProjects: RecentProjectProps[] = [
    {
      name: '  ',
      status: 'production',
      updatedAt: '2 ',
      progress: 65,
    },
    {
      name: '  ',
      status: 'feedback',
      updatedAt: '5 ',
      progress: 85,
    },
    {
      name: '  ',
      status: 'planning',
      updatedAt: '1 ',
      progress: 30,
    },
    {
      name: ' ',
      status: 'completed',
      updatedAt: '2 ',
      progress: 100,
    },
  ];

  return (
    <DashboardLayout>
      <div className="p-8">
        {/*   */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900"></h1>
          <p className="text-gray-600 mt-2">   </p>
        </div>

        {/*   */}
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

        {/*   */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/*   */}
          <Suspense 
            fallback={<SectionLoader height="h-96" />}
          >
            <RecentProjects projects={recentProjects} />
          </Suspense>

          {/*   */}
          <Suspense 
            fallback={<SectionLoader height="h-80" />}
          >
            <QuickActions />
          </Suspense>
        </div>

        {/*   */}
        <Suspense 
          fallback={<SectionLoader height="h-64" />}
        >
          <ActivityTimeline />
        </Suspense>
      </div>
    </DashboardLayout>
  );
}