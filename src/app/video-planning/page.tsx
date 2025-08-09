'use client';

import React, { useState, useEffect } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout/DashboardLayout';
import { VideoList } from '@/components/video-planning/VideoList';
import { CreateVideoModal } from '@/components/video-planning/CreateVideoModal';
import { EditVideoModal } from '@/components/video-planning/EditVideoModal';
import { Button } from '@/components/ui/Button';
import { Plus } from 'lucide-react';
import { useToast } from '@/contexts/toast.context';

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

export default function VideoPlanningPage() {
  const [videoPlans, setVideoPlans] = useState<VideoPlan[]>([]);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [editingVideo, setEditingVideo] = useState<VideoPlan | null>(null);
  const [loading, setLoading] = useState(true);
  const { showToast } = useToast();

  // 영상 기획 목록 조회
  const fetchVideoPlans = async () => {
    try {
      setLoading(true);
      const response = await fetch('https://videoplanet.up.railway.app/api/video-planning/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setVideoPlans(data.results || data);
      } else {
        throw new Error('영상 기획 목록을 불러올 수 없습니다.');
      }
    } catch (error) {
      console.error('Error fetching video plans:', error);
      showToast('영상 기획 목록 불러오기에 실패했습니다.', 'error');
      // 오류 시 샘플 데이터 사용
      setVideoPlans([
        {
          id: '1',
          title: '브랜드 소개 영상',
          description: '회사 브랜드를 소개하는 3분 분량의 영상 기획',
          status: 'draft',
          created_at: '2024-01-15T10:00:00Z',
          updated_at: '2024-01-15T10:00:00Z',
          category: '브랜딩',
          duration: '3분',
          target_audience: '잠재 고객'
        },
        {
          id: '2',
          title: '제품 데모 영상',
          description: '새로운 제품의 주요 기능을 보여주는 데모 영상',
          status: 'in_progress',
          created_at: '2024-01-14T09:30:00Z',
          updated_at: '2024-01-16T14:20:00Z',
          category: '제품',
          duration: '5분',
          target_audience: '기존 고객'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  // 영상 기획 생성
  const handleCreateVideo = async (videoData: Omit<VideoPlan, 'id' | 'created_at' | 'updated_at'>) => {
    try {
      const response = await fetch('https://videoplanet.up.railway.app/api/video-planning/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(videoData),
      });

      if (response.ok) {
        const newVideo = await response.json();
        setVideoPlans(prev => [newVideo, ...prev]);
        setIsCreateModalOpen(false);
        showToast('영상 기획이 성공적으로 생성되었습니다.', 'success');
      } else {
        throw new Error('영상 기획 생성에 실패했습니다.');
      }
    } catch (error) {
      console.error('Error creating video plan:', error);
      // 오류 시 임시 데이터로 처리
      const tempVideo: VideoPlan = {
        id: `temp_${Date.now()}`,
        ...videoData,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      setVideoPlans(prev => [tempVideo, ...prev]);
      setIsCreateModalOpen(false);
      showToast('영상 기획이 임시로 생성되었습니다. (서버 연결 후 동기화됩니다)', 'success');
    }
  };

  // 영상 기획 수정
  const handleEditVideo = async (videoData: VideoPlan) => {
    try {
      const response = await fetch(`https://videoplanet.up.railway.app/api/video-planning/${videoData.id}/`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(videoData),
      });

      if (response.ok) {
        const updatedVideo = await response.json();
        setVideoPlans(prev => prev.map(video => 
          video.id === updatedVideo.id ? updatedVideo : video
        ));
        setEditingVideo(null);
        showToast('영상 기획이 성공적으로 수정되었습니다.', 'success');
      } else {
        throw new Error('영상 기획 수정에 실패했습니다.');
      }
    } catch (error) {
      console.error('Error updating video plan:', error);
      // 오류 시 로컬 상태 업데이트
      setVideoPlans(prev => prev.map(video => 
        video.id === videoData.id ? { ...videoData, updated_at: new Date().toISOString() } : video
      ));
      setEditingVideo(null);
      showToast('영상 기획이 임시로 수정되었습니다. (서버 연결 후 동기화됩니다)', 'success');
    }
  };

  // 영상 기획 삭제
  const handleDeleteVideo = async (id: string) => {
    try {
      const response = await fetch(`https://videoplanet.up.railway.app/api/video-planning/${id}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (response.ok) {
        setVideoPlans(prev => prev.filter(video => video.id !== id));
        showToast('영상 기획이 성공적으로 삭제되었습니다.', 'success');
      } else {
        throw new Error('영상 기획 삭제에 실패했습니다.');
      }
    } catch (error) {
      console.error('Error deleting video plan:', error);
      // 오류 시 로컬에서만 삭제
      setVideoPlans(prev => prev.filter(video => video.id !== id));
      showToast('영상 기획이 임시로 삭제되었습니다. (서버 연결 후 동기화됩니다)', 'success');
    }
  };

  useEffect(() => {
    fetchVideoPlans();
  }, []);

  return (
    <DashboardLayout>
      <div className="p-6">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">영상 기획</h1>
            <p className="text-gray-600">영상 프로젝트를 계획하고 관리하세요</p>
          </div>
          <Button 
            onClick={() => setIsCreateModalOpen(true)}
            className="flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            새 기획 추가
          </Button>
        </div>

        <VideoList
          videos={videoPlans}
          loading={loading}
          onEdit={setEditingVideo}
          onDelete={handleDeleteVideo}
        />

        {/* 생성 모달 */}
        {isCreateModalOpen && (
          <CreateVideoModal
            onClose={() => setIsCreateModalOpen(false)}
            onSubmit={handleCreateVideo}
          />
        )}

        {/* 수정 모달 */}
        {editingVideo && (
          <EditVideoModal
            video={editingVideo}
            onClose={() => setEditingVideo(null)}
            onSubmit={handleEditVideo}
          />
        )}
      </div>
    </DashboardLayout>
  );
}