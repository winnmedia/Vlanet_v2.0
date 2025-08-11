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

  //    
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
        throw new Error('     .');
      }
    } catch (error) {
      console.error('Error fetching video plans:', error);
      showToast('    .', 'error');
      //     
      setVideoPlans([
        {
          id: '1',
          title: '  ',
          description: '   3   ',
          status: 'draft',
          created_at: '2024-01-15T10:00:00Z',
          updated_at: '2024-01-15T10:00:00Z',
          category: '',
          duration: '3',
          target_audience: ' '
        },
        {
          id: '2',
          title: '  ',
          description: '      ',
          status: 'in_progress',
          created_at: '2024-01-14T09:30:00Z',
          updated_at: '2024-01-16T14:20:00Z',
          category: '',
          duration: '5',
          target_audience: ' '
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  //   
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
        showToast('   .', 'success');
      } else {
        throw new Error('   .');
      }
    } catch (error) {
      console.error('Error creating video plan:', error);
      //     
      const tempVideo: VideoPlan = {
        id: `temp_${Date.now()}`,
        ...videoData,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      setVideoPlans(prev => [tempVideo, ...prev]);
      setIsCreateModalOpen(false);
      showToast('   . (   )', 'success');
    }
  };

  //   
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
        showToast('   .', 'success');
      } else {
        throw new Error('   .');
      }
    } catch (error) {
      console.error('Error updating video plan:', error);
      //     
      setVideoPlans(prev => prev.map(video => 
        video.id === videoData.id ? { ...videoData, updated_at: new Date().toISOString() } : video
      ));
      setEditingVideo(null);
      showToast('   . (   )', 'success');
    }
  };

  //   
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
        showToast('   .', 'success');
      } else {
        throw new Error('   .');
      }
    } catch (error) {
      console.error('Error deleting video plan:', error);
      //    
      setVideoPlans(prev => prev.filter(video => video.id !== id));
      showToast('   . (   )', 'success');
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
            <h1 className="text-2xl font-bold text-gray-900"> </h1>
            <p className="text-gray-600">   </p>
          </div>
          <Button 
            onClick={() => setIsCreateModalOpen(true)}
            className="flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
              
          </Button>
        </div>

        <VideoList
          videos={videoPlans}
          loading={loading}
          onEdit={setEditingVideo}
          onDelete={handleDeleteVideo}
        />

        {/*   */}
        {isCreateModalOpen && (
          <CreateVideoModal
            onClose={() => setIsCreateModalOpen(false)}
            onSubmit={handleCreateVideo}
          />
        )}

        {/*   */}
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