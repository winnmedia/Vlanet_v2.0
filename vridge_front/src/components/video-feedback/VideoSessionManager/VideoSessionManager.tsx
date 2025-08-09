'use client';

import { useState, useEffect } from 'react';
import { 
  Users, 
  Play, 
  Pause, 
  Volume2, 
  Settings, 
  UserPlus,
  UserMinus,
  Crown,
  Eye,
  Clock,
  Activity,
  Wifi,
  WifiOff
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import { videoFeedbackService } from '@/lib/api/video-feedback.service';
import type { VideoSession, User, VideoFile } from '@/types/video-feedback';
import { useToast } from '@/contexts/toast.context';

interface VideoSessionManagerProps {
  video: VideoFile;
  currentUser: User;
  session?: VideoSession;
  onSessionChange?: (session: VideoSession | null) => void;
  onUserJoin?: (user: User) => void;
  onUserLeave?: (userId: number) => void;
  className?: string;
}

interface SessionSettings {
  allowComments: boolean;
  syncPlayback: boolean;
  autoPauseOnFeedback: boolean;
  maxParticipants: number;
  requireApproval: boolean;
}

export default function VideoSessionManager({
  video,
  currentUser,
  session,
  onSessionChange,
  onUserJoin,
  onUserLeave,
  className = ''
}: VideoSessionManagerProps) {
  const { success, error } = useToast();
  
  const [isConnected, setIsConnected] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showParticipants, setShowParticipants] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected'>('disconnected');
  
  const [sessionSettings, setSessionSettings] = useState<SessionSettings>({
    allowComments: true,
    syncPlayback: true,
    autoPauseOnFeedback: true,
    maxParticipants: 10,
    requireApproval: false
  });

  // 세션 생성
  const createSession = async () => {
    try {
      setConnectionStatus('connecting');
      
      const result = await videoFeedbackService.createVideoSession({
        video_id: video.id,
        title: `${video.title} - 실시간 협업`,
        settings: {
          allow_comments: sessionSettings.allowComments,
          sync_playback: sessionSettings.syncPlayback,
          auto_pause_on_feedback: sessionSettings.autoPauseOnFeedback
        }
      });

      if (result.success && result.data) {
        onSessionChange?.(result.data);
        setConnectionStatus('connected');
        setIsConnected(true);
        success('협업 세션을 시작했습니다.');
      }
    } catch (err) {
      setConnectionStatus('disconnected');
      error('세션 생성에 실패했습니다.');
    }
  };

  // 세션 참여
  const joinSession = async () => {
    if (!session) return;
    
    try {
      setConnectionStatus('connecting');
      
      const result = await videoFeedbackService.joinSession(session.id);
      if (result.success) {
        setConnectionStatus('connected');
        setIsConnected(true);
        success('세션에 참여했습니다.');
      }
    } catch (err) {
      setConnectionStatus('disconnected');
      error('세션 참여에 실패했습니다.');
    }
  };

  // 세션 떠나기
  const leaveSession = async () => {
    if (!session) return;
    
    try {
      await videoFeedbackService.leaveSession(session.id);
      onSessionChange?.(null);
      setConnectionStatus('disconnected');
      setIsConnected(false);
      success('세션에서 나갔습니다.');
    } catch (err) {
      error('세션 떠나기에 실패했습니다.');
    }
  };

  // 연결 상태 표시 컴포넌트
  const ConnectionIndicator = () => (
    <div className="flex items-center gap-2">
      {connectionStatus === 'connected' ? (
        <>
          <Wifi size={16} className="text-green-500" />
          <span className="text-sm text-green-600">연결됨</span>
        </>
      ) : connectionStatus === 'connecting' ? (
        <>
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500" />
          <span className="text-sm text-blue-600">연결중...</span>
        </>
      ) : (
        <>
          <WifiOff size={16} className="text-gray-400" />
          <span className="text-sm text-gray-500">연결 안됨</span>
        </>
      )}
    </div>
  );

  // 참여자 역할 아이콘
  const getRoleIcon = (user: User, isHost: boolean) => {
    if (isHost) return <Crown size={14} className="text-yellow-500" />;
    return <Eye size={14} className="text-gray-400" />;
  };

  // 참여자 색상
  const getUserColor = (userId: number) => {
    const colors = [
      'bg-red-500', 'bg-blue-500', 'bg-green-500', 'bg-yellow-500',
      'bg-purple-500', 'bg-pink-500', 'bg-indigo-500', 'bg-orange-500'
    ];
    return colors[userId % colors.length];
  };

  // 실시간 상태 업데이트 (WebSocket 시뮬레이션)
  useEffect(() => {
    if (!session || !isConnected) return;

    // 실제로는 WebSocket을 통해 실시간 업데이트를 받아야 함
    const interval = setInterval(() => {
      // 세션 상태 업데이트 로직
    }, 5000);

    return () => clearInterval(interval);
  }, [session, isConnected]);

  return (
    <div className={`bg-white border rounded-lg shadow-sm ${className}`}>
      {/* 헤더 */}
      <div className="p-4 border-b">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Users size={20} className="text-blue-600" />
            <div>
              <h3 className="font-medium text-gray-800">실시간 협업</h3>
              <div className="text-sm text-gray-500">
                <ConnectionIndicator />
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowSettings(true)}
            >
              <Settings size={16} />
            </Button>
            
            {session && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowParticipants(true)}
                className="flex items-center gap-1"
              >
                <Users size={16} />
                {session.participants.length}
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* 세션 상태 */}
      <div className="p-4">
        {!session ? (
          <div className="text-center py-6">
            <Users size={48} className="mx-auto mb-4 text-gray-300" />
            <h4 className="text-lg font-medium text-gray-600 mb-2">협업 세션 없음</h4>
            <p className="text-sm text-gray-500 mb-4">
              새 협업 세션을 시작하거나 기존 세션에 참여하세요.
            </p>
            <Button
              onClick={createSession}
              disabled={connectionStatus === 'connecting'}
              className="bg-blue-600 hover:bg-blue-700 text-white"
            >
              {connectionStatus === 'connecting' ? '생성중...' : '새 세션 시작'}
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            {/* 세션 정보 */}
            <div className="p-3 bg-blue-50 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Activity size={16} className="text-blue-600" />
                <span className="font-medium text-blue-800">{session.title}</span>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">호스트:</span>
                  <span className="ml-2 font-medium">
                    {session.host.first_name} {session.host.last_name}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">참여자:</span>
                  <span className="ml-2 font-medium">{session.participants.length}명</span>
                </div>
              </div>
            </div>

            {/* 참여자 미리보기 */}
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600">참여중:</span>
              <div className="flex -space-x-2">
                {session.participants.slice(0, 5).map((participant) => (
                  <div
                    key={participant.id}
                    className={`w-8 h-8 rounded-full border-2 border-white flex items-center justify-center text-white text-xs font-bold ${getUserColor(participant.id)}`}
                    title={`${participant.first_name} ${participant.last_name}`}
                  >
                    {participant.first_name[0]}{participant.last_name[0]}
                  </div>
                ))}
                {session.participants.length > 5 && (
                  <div className="w-8 h-8 rounded-full border-2 border-white bg-gray-400 flex items-center justify-center text-white text-xs font-bold">
                    +{session.participants.length - 5}
                  </div>
                )}
              </div>
            </div>

            {/* 현재 재생 상태 */}
            {session.playback_state && (
              <div className="p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3 text-sm">
                  <div className="flex items-center gap-1">
                    {session.playback_state.is_playing ? (
                      <Play size={14} className="text-green-500" />
                    ) : (
                      <Pause size={14} className="text-gray-500" />
                    )}
                    <span className={session.playback_state.is_playing ? 'text-green-600' : 'text-gray-600'}>
                      {session.playback_state.is_playing ? '재생중' : '일시정지'}
                    </span>
                  </div>
                  
                  <div className="flex items-center gap-1">
                    <Clock size={14} className="text-blue-500" />
                    <span className="text-blue-600">
                      {Math.floor(session.playback_state.current_time / 60)}:
                      {(session.playback_state.current_time % 60).toString().padStart(2, '0')}
                    </span>
                  </div>
                  
                  <span className="text-gray-500 text-xs ml-auto">
                    {session.playback_state.playback_rate}x 속도
                  </span>
                </div>
              </div>
            )}

            {/* 세션 컨트롤 */}
            <div className="flex gap-2">
              {isConnected ? (
                <Button
                  onClick={leaveSession}
                  variant="ghost"
                  className="flex-1 text-red-600 hover:bg-red-50"
                >
                  <UserMinus size={16} className="mr-2" />
                  세션 떠나기
                </Button>
              ) : (
                <Button
                  onClick={joinSession}
                  disabled={connectionStatus === 'connecting'}
                  className="flex-1 bg-green-600 hover:bg-green-700 text-white"
                >
                  <UserPlus size={16} className="mr-2" />
                  {connectionStatus === 'connecting' ? '참여중...' : '세션 참여'}
                </Button>
              )}
            </div>
          </div>
        )}
      </div>

      {/* 참여자 모달 */}
      <Modal
        isOpen={showParticipants}
        onClose={() => setShowParticipants(false)}
        title="참여자 목록"
      >
        {session && (
          <div className="space-y-3">
            {session.participants.map((participant) => (
              <div key={participant.id} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white font-bold ${getUserColor(participant.id)}`}>
                  {participant.first_name[0]}{participant.last_name[0]}
                </div>
                
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-gray-800">
                      {participant.first_name} {participant.last_name}
                    </span>
                    {getRoleIcon(participant, session.host.id === participant.id)}
                    {session.host.id === participant.id && (
                      <span className="text-xs bg-yellow-100 text-yellow-700 px-2 py-1 rounded-full">
                        호스트
                      </span>
                    )}
                  </div>
                  <div className="text-sm text-gray-500">{participant.email}</div>
                </div>
                
                <div className="text-xs text-gray-400">
                  {participant.id === currentUser.id ? '나' : '참여자'}
                </div>
              </div>
            ))}
          </div>
        )}
      </Modal>

      {/* 설정 모달 */}
      <Modal
        isOpen={showSettings}
        onClose={() => setShowSettings(false)}
        title="세션 설정"
      >
        <div className="space-y-4">
          <div className="space-y-3">
            <label className="flex items-center gap-3">
              <input
                type="checkbox"
                checked={sessionSettings.allowComments}
                onChange={(e) => setSessionSettings(prev => ({ ...prev, allowComments: e.target.checked }))}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <div>
                <div className="font-medium text-gray-800">실시간 채팅 허용</div>
                <div className="text-sm text-gray-500">참여자가 실시간으로 채팅할 수 있습니다.</div>
              </div>
            </label>

            <label className="flex items-center gap-3">
              <input
                type="checkbox"
                checked={sessionSettings.syncPlayback}
                onChange={(e) => setSessionSettings(prev => ({ ...prev, syncPlayback: e.target.checked }))}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <div>
                <div className="font-medium text-gray-800">재생 동기화</div>
                <div className="text-sm text-gray-500">모든 참여자의 재생 상태를 동기화합니다.</div>
              </div>
            </label>

            <label className="flex items-center gap-3">
              <input
                type="checkbox"
                checked={sessionSettings.autoPauseOnFeedback}
                onChange={(e) => setSessionSettings(prev => ({ ...prev, autoPauseOnFeedback: e.target.checked }))}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <div>
                <div className="font-medium text-gray-800">피드백 작성 시 자동 정지</div>
                <div className="text-sm text-gray-500">누군가 피드백을 작성하면 영상이 자동으로 정지됩니다.</div>
              </div>
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              최대 참여자 수
            </label>
            <input
              type="number"
              min="2"
              max="20"
              value={sessionSettings.maxParticipants}
              onChange={(e) => setSessionSettings(prev => ({ ...prev, maxParticipants: parseInt(e.target.value) }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div className="flex gap-3 pt-4 border-t">
            <Button
              onClick={() => setShowSettings(false)}
              className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
            >
              저장
            </Button>
            <Button
              variant="ghost"
              onClick={() => setShowSettings(false)}
              className="px-6"
            >
              취소
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}