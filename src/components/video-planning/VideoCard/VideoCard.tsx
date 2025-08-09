'use client';

import React from 'react';
import { Edit, Trash2, Clock, Users, Play } from 'lucide-react';
import { cn } from '@/lib/cn';

interface VideoPlan {
  id: string;
  title: string;
  description: string;
  status: 'draft' | 'in_progress' | 'completed';
  created_at: string;
  updated_at: string;
  category: string;
  duration: string;
  target_audience: string;
}

interface VideoCardProps {
  video: VideoPlan;
  onEdit: () => void;
  onDelete: () => void;
}

const statusConfig = {
  draft: {
    label: '초안',
    color: 'bg-gray-100 text-gray-800',
    icon: '📝'
  },
  in_progress: {
    label: '진행 중',
    color: 'bg-blue-100 text-blue-800',
    icon: '⚡'
  },
  completed: {
    label: '완료',
    color: 'bg-green-100 text-green-800',
    icon: '✅'
  }
};

export function VideoCard({ video, onEdit, onDelete }: VideoCardProps) {
  const status = statusConfig[video.status];
  const createdDate = new Date(video.created_at).toLocaleDateString('ko-KR');

  const handleDelete = () => {
    if (window.confirm('정말로 이 영상 기획을 삭제하시겠습니까?')) {
      onDelete();
    }
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 hover:shadow-md transition-shadow">
      {/* 카드 헤더 */}
      <div className="p-4 border-b border-gray-100">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="font-semibold text-gray-900 text-lg mb-1 line-clamp-1">
              {video.title}
            </h3>
            <div className="flex items-center gap-2">
              <span className={cn(
                "inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium",
                status.color
              )}>
                <span>{status.icon}</span>
                {status.label}
              </span>
              <span className="text-xs text-gray-500">{video.category}</span>
            </div>
          </div>
          <div className="flex gap-1 ml-2">
            <button
              onClick={onEdit}
              className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
              title="수정"
            >
              <Edit className="h-4 w-4" />
            </button>
            <button
              onClick={handleDelete}
              className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
              title="삭제"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      {/* 카드 본문 */}
      <div className="p-4">
        <p className="text-gray-600 text-sm mb-4 line-clamp-3">
          {video.description}
        </p>

        <div className="space-y-2">
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <Clock className="h-4 w-4" />
            <span>영상 길이: {video.duration}</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <Users className="h-4 w-4" />
            <span>타겟: {video.target_audience}</span>
          </div>
        </div>

        <div className="mt-4 pt-4 border-t border-gray-100">
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>생성일: {createdDate}</span>
            {video.status === 'in_progress' && (
              <div className="flex items-center gap-1 text-blue-600">
                <Play className="h-3 w-3" />
                <span className="font-medium">진행 중</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}