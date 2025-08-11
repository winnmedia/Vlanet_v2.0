'use client';

import React from 'react';
import { VideoCard } from '../VideoCard';
import { Spinner } from '@/components/ui/Spinner';

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

interface VideoListProps {
  videos: VideoPlan[];
  loading: boolean;
  onEdit: (video: VideoPlan) => void;
  onDelete: (id: string) => void;
}

export function VideoList({ videos, loading, onEdit, onDelete }: VideoListProps) {
  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  if (videos.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="bg-gray-50 rounded-lg p-8">
          <div className="text-gray-400 text-4xl mb-4"></div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
               
          </h3>
          <p className="text-gray-500">
                
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {videos.map((video) => (
        <VideoCard
          key={video.id}
          video={video}
          onEdit={() => onEdit(video)}
          onDelete={() => onDelete(video.id)}
        />
      ))}
    </div>
  );
}