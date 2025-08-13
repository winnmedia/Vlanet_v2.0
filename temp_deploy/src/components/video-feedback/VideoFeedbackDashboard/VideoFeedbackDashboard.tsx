'use client';

import { useState, useEffect } from 'react';
import { 
  Play,
  Users,
  MessageSquare,
  Clock,
  TrendingUp,
  Filter,
  Download,
  Share2,
  Settings,
  ChevronLeft,
  ChevronRight,
  BarChart3,
  PieChart,
  Activity,
  CheckCircle2,
  AlertCircle,
  XCircle
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import VideoPlayer from '../VideoPlayer';
import TimelineFeedback from '../TimelineFeedback';
import RealtimeComments from '../RealtimeComments';
import { videoFeedbackService } from '@/lib/api/video-feedback.service';
import type { 
  VideoFile, 
  TimelineFeedback as TimelineFeedbackType, 
  VideoSession,
  RealtimeComment,
  VideoFeedbackStats,
  User,
  CreateTimelineFeedbackData,
  CreateRealtimeCommentData
} from '@/types/video-feedback';
import { useToast } from '@/contexts/toast.context';

interface VideoFeedbackDashboardProps {
  videoId: string;
  projectId?: number;
  currentUser: User;
  className?: string;
}

interface DashboardTab {
  id: string;
  label: string;
  icon: React.ReactNode;
}

const TABS: DashboardTab[] = [
  { id: 'overview', label: '개요', icon: <BarChart3 size={16} /> },
  { id: 'timeline', label: '타임라인', icon: <Clock size={16} /> },
  { id: 'chat', label: '실시간 채팅', icon: <MessageSquare size={16} /> },
  { id: 'analytics', label: '분석', icon: <PieChart size={16} /> }
];

export default function VideoFeedbackDashboard({ 
  videoId, 
  projectId, 
  currentUser,
  className = '' 
}: VideoFeedbackDashboardProps) {
  const { success, error } = useToast();
  
  // 상태 관리
  const [video, setVideo] = useState<VideoFile | null>(null);
  const [feedbacks, setFeedbacks] = useState<TimelineFeedbackType[]>([]);
  const [session, setSession] = useState<VideoSession | null>(null);
  const [comments, setComments] = useState<RealtimeComment[]>([]);
  const [stats, setStats] = useState<VideoFeedbackStats | null>(null);
  const [mentionableUsers, setMentionableUsers] = useState<User[]>([]);
  
  const [activeTab, setActiveTab] = useState('overview');
  const [isLoading, setIsLoading] = useState(true);
  const [currentTime, setCurrentTime] = useState(0);
  const [isCollaborationMode, setIsCollaborationMode] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  // 데이터 로딩
  useEffect(() => {
    loadDashboardData();
  }, [videoId]);

  const loadDashboardData = async () => {
    setIsLoading(true);
    try {
      // 병렬로 데이터 로드
      const [
        videoResult,
        feedbacksResult,
        sessionsResult,
        statsResult,
        usersResult
      ] = await Promise.all([
        videoFeedbackService.getVideo(videoId),
        videoFeedbackService.getVideoFeedbacks(videoId),
        videoFeedbackService.getVideoSessions(videoId),
        videoFeedbackService.getVideoFeedbackStats(videoId),
        videoFeedbackService.getMentionableUsers(videoId)
      ]);

      if (videoResult.success && videoResult.data) {
        setVideo(videoResult.data);
      }

      if (feedbacksResult.success && feedbacksResult.data) {
        setFeedbacks(feedbacksResult.data);
      }

      if (sessionsResult.success && sessionsResult.data) {
        const activeSessions = sessionsResult.data.filter(s => s.is_active);
        if (activeSessions.length > 0) {
          setSession(activeSessions[0]);
          loadSessionComments(activeSessions[0].id);
        }
      }

      if (statsResult.success && statsResult.data) {
        setStats(statsResult.data);
      }

      if (usersResult.success && usersResult.data) {
        setMentionableUsers(usersResult.data);
      }
    } catch (err) {
      console.error('대시보드 데이터 로딩 실패:', err);
      error('데이터를 불러오는데 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const loadSessionComments = async (sessionId: string) => {
    try {
      const result = await videoFeedbackService.getSessionComments(sessionId, 50);
      if (result.success && result.data) {
        setComments(result.data);
      }
    } catch (err) {
      console.error('코멘트 로딩 실패:', err);
    }
  };

  // 협업 세션 시작/종료
  const toggleCollaborationMode = async () => {
    if (!video) return;

    try {
      if (isCollaborationMode && session) {
        // 세션 종료
        await videoFeedbackService.leaveSession(session.id);
        setSession(null);
        setComments([]);
        setIsCollaborationMode(false);
        success('협업 모드를 종료했습니다.');
      } else {
        // 새 세션 생성
        const result = await videoFeedbackService.createVideoSession({
          video_id: videoId,
          title: `${video.title} - 실시간 협업`,
          settings: {
            allow_comments: true,
            sync_playback: true,
            auto_pause_on_feedback: true
          }
        });

        if (result.success && result.data) {
          setSession(result.data);
          setIsCollaborationMode(true);
          success('협업 모드를 시작했습니다.');
        }
      }
    } catch (err) {
      error('협업 모드 전환에 실패했습니다.');
    }
  };

  // 피드백 관련 핸들러
  const handleCreateFeedback = async (data: CreateTimelineFeedbackData) => {
    try {
      const result = await videoFeedbackService.createFeedback(data);
      if (result.success && result.data) {
        setFeedbacks(prev => [...prev, result.data]);
        success('피드백이 추가되었습니다.');
      }
    } catch (err) {
      error('피드백 추가에 실패했습니다.');
    }
  };

  const handleUpdateFeedback = async (id: string, data: Partial<TimelineFeedbackType>) => {
    try {
      const result = await videoFeedbackService.updateFeedback(id, data);
      if (result.success && result.data) {
        setFeedbacks(prev => prev.map(f => f.id === id ? result.data : f));
        success('피드백이 수정되었습니다.');
      }
    } catch (err) {
      error('피드백 수정에 실패했습니다.');
    }
  };

  const handleDeleteFeedback = async (id: string) => {
    if (!window.confirm('정말로 이 피드백을 삭제하시겠습니까?')) return;

    try {
      const result = await videoFeedbackService.deleteFeedback(id);
      if (result.success) {
        setFeedbacks(prev => prev.filter(f => f.id !== id));
        success('피드백이 삭제되었습니다.');
      }
    } catch (err) {
      error('피드백 삭제에 실패했습니다.');
    }
  };

  const handleFeedbackClick = (feedback: TimelineFeedbackType) => {
    setCurrentTime(feedback.timestamp);
    if (activeTab !== 'timeline') {
      setActiveTab('timeline');
    }
  };

  const handleAddFeedbackAtTime = (timestamp: number, position?: { x: number; y: number }) => {
    setCurrentTime(timestamp);
    setActiveTab('timeline');
    // 타임라인 컴포넌트에서 피드백 생성 모달이 열리도록 추가 로직 필요
  };

  // 실시간 코멘트 핸들러
  const handleSendComment = async (data: CreateRealtimeCommentData) => {
    if (!session) return;

    try {
      const result = await videoFeedbackService.createComment(data);
      if (result.success && result.data) {
        setComments(prev => [...prev, result.data]);
      }
    } catch (err) {
      error('메시지 전송에 실패했습니다.');
    }
  };

  const handleDeleteComment = async (commentId: string) => {
    // API에서 삭제 후 상태 업데이트
    setComments(prev => prev.filter(c => c.id !== commentId));
  };

  // 재생 상태 동기화
  const handlePlaybackSync = async (playbackState: {
    currentTime: number;
    isPlaying: boolean;
    playbackRate: number;
  }) => {
    if (session && isCollaborationMode) {
      try {
        await videoFeedbackService.syncPlayback(session.id, playbackState);
      } catch (err) {
        console.error('재생 상태 동기화 실패:', err);
      }
    }
  };

  // 통계 카드 렌더링
  const renderStatsCards = () => {
    if (!stats) return null;

    const cards = [
      {
        title: '전체 피드백',
        value: stats.total_feedbacks,
        icon: <MessageSquare size={24} />,
        color: 'bg-blue-500'
      },
      {
        title: '해결률',
        value: `${Math.round(stats.resolution_rate * 100)}%`,
        icon: <CheckCircle2 size={24} />,
        color: 'bg-green-500'
      },
      {
        title: '활성 피드백',
        value: stats.by_status.active || 0,
        icon: <AlertCircle size={24} />,
        color: 'bg-orange-500'
      },
      {
        title: '참여자',
        value: mentionableUsers.length,
        icon: <Users size={24} />,
        color: 'bg-purple-500'
      }
    ];

    return (
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        {cards.map((card, index) => (
          <div key={index} className="bg-white p-4 rounded-lg shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">{card.title}</p>
                <p className="text-2xl font-bold text-gray-800">{card.value}</p>
              </div>
              <div className={`p-3 rounded-full ${card.color} text-white`}>
                {card.icon}
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  };

  // 분석 차트 렌더링
  const renderAnalytics = () => {
    if (!stats) return <div>데이터를 불러오는 중...</div>;

    return (
      <div className="space-y-6">
        {/* 카테고리별 분포 */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h4 className="text-lg font-semibold mb-4">카테고리별 피드백 분포</h4>
          <div className="space-y-3">
            {Object.entries(stats.by_category).map(([category, count]) => (
              <div key={category} className="flex items-center justify-between">
                <span className="text-sm text-gray-600 capitalize">{category}</span>
                <div className="flex items-center gap-2">
                  <div className="w-24 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-500 h-2 rounded-full"
                      style={{ width: `${(count / stats.total_feedbacks) * 100}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium w-8 text-right">{count}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 핫스팟 */}
        {stats.most_commented_timestamps.length > 0 && (
          <div className="bg-white p-6 rounded-lg shadow">
            <h4 className="text-lg font-semibold mb-4">가장 많이 코멘트된 구간</h4>
            <div className="space-y-3">
              {stats.most_commented_timestamps.slice(0, 5).map((hotspot, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-red-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                      {index + 1}
                    </div>
                    <div>
                      <div className="font-medium">
                        {Math.floor(hotspot.timestamp / 60)}:{(hotspot.timestamp % 60).toString().padStart(2, '0')}
                      </div>
                      <div className="text-sm text-gray-500">{hotspot.count}개 피드백</div>
                    </div>
                  </div>
                  <Button 
                    size="sm" 
                    variant="ghost"
                    onClick={() => setCurrentTime(hotspot.timestamp)}
                  >
                    이동
                  </Button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!video) {
    return (
      <div className="flex items-center justify-center h-96 text-gray-500">
        <div className="text-center">
          <XCircle size={48} className="mx-auto mb-4 opacity-50" />
          <h3 className="text-lg font-medium">영상을 찾을 수 없습니다</h3>
          <p className="text-sm">영상 ID를 확인해주세요.</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`flex flex-col h-screen bg-gray-50 ${className}`}>
      {/* 헤더 */}
      <div className="bg-white border-b px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-2xl font-bold text-gray-800">{video.title}</h1>
            {session && (
              <div className="flex items-center gap-2 px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm">
                <Activity size={16} />
                실시간 협업중 ({session.participants.length}명)
              </div>
            )}
          </div>
          
          <div className="flex items-center gap-3">
            <Button
              variant={isCollaborationMode ? "default" : "ghost"}
              onClick={toggleCollaborationMode}
              className={isCollaborationMode ? "bg-green-600 hover:bg-green-700 text-white" : ""}
            >
              <Users size={16} className="mr-2" />
              {isCollaborationMode ? '협업 종료' : '협업 시작'}
            </Button>
            
            <Button variant="ghost">
              <Share2 size={16} className="mr-2" />
              공유
            </Button>
            
            <Button variant="ghost">
              <Download size={16} className="mr-2" />
              내보내기
            </Button>
            
            <Button variant="ghost">
              <Settings size={16} />
            </Button>
          </div>
        </div>
      </div>

      {/* 메인 콘텐츠 */}
      <div className="flex flex-1 overflow-hidden">
        {/* 비디오 플레이어 영역 */}
        <div className="flex-1 flex flex-col">
          {/* 비디오 플레이어 */}
          <div className="bg-black p-6">
            <VideoPlayer
              video={video}
              feedbacks={feedbacks}
              session={session || undefined}
              currentTime={currentTime}
              onTimeUpdate={setCurrentTime}
              onFeedbackClick={handleFeedbackClick}
              onAddFeedback={handleAddFeedbackAtTime}
              onPlaybackSync={handlePlaybackSync}
              syncEnabled={isCollaborationMode}
              showFeedbackMarkers={true}
              allowNewFeedbacks={true}
              className="max-h-[60vh]"
            />
          </div>

          {/* 탭 네비게이션 */}
          <div className="bg-white border-b">
            <div className="flex">
              {TABS.map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-6 py-3 text-sm font-medium transition-colors ${
                    activeTab === tab.id
                      ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  {tab.icon}
                  {tab.label}
                </button>
              ))}
            </div>
          </div>

          {/* 탭 콘텐츠 */}
          <div className="flex-1 overflow-hidden p-6">
            {activeTab === 'overview' && (
              <div>
                {renderStatsCards()}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="bg-white p-6 rounded-lg shadow">
                    <h3 className="text-lg font-semibold mb-4">최근 피드백</h3>
                    <div className="space-y-3">
                      {feedbacks.slice(0, 5).map(feedback => (
                        <div key={feedback.id} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                          <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                          <div className="flex-1">
                            <div className="font-medium text-sm">{feedback.title}</div>
                            <div className="text-xs text-gray-500">
                              {Math.floor(feedback.timestamp / 60)}:{(feedback.timestamp % 60).toString().padStart(2, '0')} - {feedback.author.first_name}
                            </div>
                          </div>
                          <Button size="sm" variant="ghost" onClick={() => handleFeedbackClick(feedback)}>
                            이동
                          </Button>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div className="bg-white p-6 rounded-lg shadow">
                    <h3 className="text-lg font-semibold mb-4">진행 상황</h3>
                    {stats && (
                      <div className="space-y-4">
                        <div>
                          <div className="flex justify-between text-sm mb-2">
                            <span>해결된 피드백</span>
                            <span>{stats.by_status.resolved || 0}/{stats.total_feedbacks}</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-green-500 h-2 rounded-full"
                              style={{ width: `${stats.resolution_rate * 100}%` }}
                            />
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-3 gap-4 pt-4 border-t">
                          <div className="text-center">
                            <div className="text-2xl font-bold text-blue-600">{stats.by_status.active || 0}</div>
                            <div className="text-xs text-gray-500">활성</div>
                          </div>
                          <div className="text-center">
                            <div className="text-2xl font-bold text-green-600">{stats.by_status.resolved || 0}</div>
                            <div className="text-xs text-gray-500">해결</div>
                          </div>
                          <div className="text-center">
                            <div className="text-2xl font-bold text-gray-600">{stats.by_status.declined || 0}</div>
                            <div className="text-xs text-gray-500">거부</div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'analytics' && renderAnalytics()}
          </div>
        </div>

        {/* 사이드바 */}
        <div className={`bg-white border-l transition-all duration-300 ${sidebarCollapsed ? 'w-0' : 'w-96'} flex flex-col`}>
          {!sidebarCollapsed && (
            <>
              {activeTab === 'timeline' && (
                <TimelineFeedback
                  feedbacks={feedbacks}
                  currentTime={currentTime}
                  onFeedbackClick={handleFeedbackClick}
                  onCreateFeedback={handleCreateFeedback}
                  onUpdateFeedback={handleUpdateFeedback}
                  onDeleteFeedback={handleDeleteFeedback}
                  mentionableUsers={mentionableUsers}
                  className="flex-1"
                />
              )}

              {activeTab === 'chat' && session && (
                <RealtimeComments
                  session={session}
                  comments={comments}
                  currentUser={currentUser}
                  currentTime={currentTime}
                  onSendComment={handleSendComment}
                  onDeleteComment={handleDeleteComment}
                  className="flex-1"
                />
              )}

              {(activeTab === 'overview' || activeTab === 'analytics') && (
                <div className="p-4 text-center text-gray-500">
                  <MessageSquare size={48} className="mx-auto mb-4 opacity-50" />
                  <p>다른 탭을 선택해서 상호작용하세요</p>
                </div>
              )}
            </>
          )}

          {/* 사이드바 토글 */}
          <button
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className="absolute top-1/2 -left-3 transform -translate-y-1/2 bg-white border rounded-full p-1 shadow-md hover:shadow-lg transition-shadow z-10"
          >
            {sidebarCollapsed ? <ChevronLeft size={16} /> : <ChevronRight size={16} />}
          </button>
        </div>
      </div>
    </div>
  );
}