'use client';

import React from 'react';
import Link from 'next/link';
import { cn } from '@/lib/cn';

// 최근 프로젝트 아이템
interface RecentProjectProps {
  name: string;
  status: 'planning' | 'production' | 'feedback' | 'completed';
  updatedAt: string;
  progress: number;
}

const RecentProject: React.FC<RecentProjectProps> = ({ 
  name, 
  status, 
  updatedAt, 
  progress 
}) => {
  const statusLabels = {
    planning: { text: '기획중', color: 'bg-blue-100 text-blue-700' },
    production: { text: '제작중', color: 'bg-yellow-100 text-yellow-700' },
    feedback: { text: '피드백', color: 'bg-purple-100 text-purple-700' },
    completed: { text: '완료', color: 'bg-green-100 text-green-700' },
  };

  const statusConfig = statusLabels[status];

  return (
    <div className="flex items-center justify-between p-4 hover:bg-gray-50 rounded-lg transition-colors">
      <div className="flex-1">
        <h4 className="font-medium text-gray-900">{name}</h4>
        <div className="flex items-center gap-4 mt-2">
          <span className={cn(
            "text-xs px-2 py-1 rounded-full font-medium",
            statusConfig.color
          )}>
            {statusConfig.text}
          </span>
          <span className="text-xs text-gray-500">{updatedAt}</span>
        </div>
      </div>
      <div className="w-32">
        <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
          <span>진행률</span>
          <span>{progress}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-brand-primary h-2 rounded-full transition-all"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>
    </div>
  );
};

interface RecentProjectsProps {
  projects: RecentProjectProps[];
}

const RecentProjects: React.FC<RecentProjectsProps> = ({ projects }) => {
  return (
    <div className="lg:col-span-2 bg-white rounded-lg border border-gray-200">
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">최근 프로젝트</h2>
          <Link 
            href="/projects" 
            className="text-sm text-brand-primary hover:text-brand-primary-dark"
          >
            모두 보기 →
          </Link>
        </div>
      </div>
      <div className="p-6 space-y-2">
        {projects.map((project, index) => (
          <RecentProject key={index} {...project} />
        ))}
      </div>
    </div>
  );
};

export default RecentProjects;