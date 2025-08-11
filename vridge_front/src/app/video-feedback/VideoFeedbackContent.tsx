'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import DashboardLayout from '@/components/layout/DashboardLayout';
import VideoFeedbackDashboard from '@/components/video-feedback/VideoFeedbackDashboard';
import { useAuthStore } from '@/store/auth.store';
import { videoFeedbackService } from '@/lib/api/video-feedback.service';
import type { VideoFile, User } from '@/types/video-feedback';
import { useToast } from '@/contexts/toast.context';

export default function VideoFeedbackContent() {
  const { user, isAuthenticated } = useAuthStore();
  const { error } = useToast();
  const searchParams = useSearchParams();
  
  const [videos, setVideos] = useState<VideoFile[]>([]);
  const [selectedVideo, setSelectedVideo] = useState<VideoFile | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // URL   ID 
  const videoIdFromUrl = searchParams.get('video');
  const projectIdFromUrl = searchParams.get('project');

  useEffect(() => {
    if (!isAuthenticated) {
      //   
      window.location.href = '/login';
      return;
    }
    
    loadVideos();
  }, [isAuthenticated]);

  //   ID URL    
  useEffect(() => {
    if (videoIdFromUrl && videos.length > 0) {
      const video = videos.find(v => v.id === videoIdFromUrl);
      if (video) {
        setSelectedVideo(video);
      }
    }
  }, [videoIdFromUrl, videos]);

  const loadVideos = async () => {
    try {
      setIsLoading(true);
      
      const projectId = projectIdFromUrl ? parseInt(projectIdFromUrl) : undefined;
      const result = await videoFeedbackService.getVideos(projectId);
      
      if (result.success && result.data) {
        setVideos(result.data);
        
        //      (URL   )
        if (!videoIdFromUrl && result.data.length > 0) {
          setSelectedVideo(result.data[0]);
        }
      } else {
        //   (API   )
        const sampleVideos: VideoFile[] = [
          {
            id: 'sample-1',
            title: '   v1.2',
            description: '     ',
            file_url: '/sample-video.mp4', //     URL
            thumbnail_url: '/sample-thumbnail.jpg',
            duration: 180, // 3
            resolution: '1920x1080',
            file_size: 85000000, // 85MB
            format: 'mp4',
            project_id: projectId,
            created_at: '2024-01-15T09:00:00Z',
            updated_at: '2024-01-15T12:30:00Z'
          },
          {
            id: 'sample-2',
            title: '  ',
            description: '    ',
            file_url: '/sample-video-2.mp4',
            thumbnail_url: '/sample-thumbnail-2.jpg',
            duration: 240, // 4
            resolution: '1920x1080',
            file_size: 120000000, // 120MB
            format: 'mp4',
            project_id: projectId,
            created_at: '2024-01-16T10:00:00Z',
            updated_at: '2024-01-16T14:20:00Z'
          }
        ];
        
        setVideos(sampleVideos);
        if (!videoIdFromUrl && sampleVideos.length > 0) {
          setSelectedVideo(sampleVideos[0]);
        }
      }
    } catch (err) {
      console.error('   :', err);
      error('   .');
    } finally {
      setIsLoading(false);
    }
  };

  if (!isAuthenticated || !user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-96">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </DashboardLayout>
    );
  }

  if (videos.length === 0) {
    return (
      <DashboardLayout>
        <div className="flex flex-col items-center justify-center h-96">
          <div className="text-center">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2"> </h3>
            <p className="text-gray-500 mb-4">    .</p>
            <button 
              onClick={() => window.location.href = '/video-planning'}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
            >
                 
            </button>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (!selectedVideo) {
    return (
      <DashboardLayout>
        <div className="p-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">  </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {videos.map((video) => (
              <div
                key={video.id}
                className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => setSelectedVideo(video)}
              >
                <div className="aspect-video bg-gray-200 rounded-t-lg flex items-center justify-center">
                  {video.thumbnail_url ? (
                    <img 
                      src={video.thumbnail_url} 
                      alt={video.title}
                      className="w-full h-full object-cover rounded-t-lg"
                    />
                  ) : (
                    <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h.01M19 10a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  )}
                </div>
                
                <div className="p-4">
                  <h3 className="font-semibold text-gray-800 mb-2 line-clamp-2">{video.title}</h3>
                  {video.description && (
                    <p className="text-sm text-gray-600 mb-3 line-clamp-2">{video.description}</p>
                  )}
                  
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>{Math.floor(video.duration / 60)}:{(video.duration % 60).toString().padStart(2, '0')}</span>
                    <span>{video.resolution}</span>
                    <span>{(video.file_size / 1000000).toFixed(1)}MB</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </DashboardLayout>
    );
  }

  // user     
  const currentUserData: User = user || {
    id: 'guest',
    username: 'Guest User',
    email: 'guest@example.com',
    avatar_url: undefined,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  };

  return (
    <VideoFeedbackDashboard
      videoId={selectedVideo.id}
      projectId={selectedVideo.project_id}
      currentUser={currentUserData}
      className="h-screen"
    />
  );
}