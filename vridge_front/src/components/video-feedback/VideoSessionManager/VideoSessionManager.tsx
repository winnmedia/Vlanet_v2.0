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

  //  
  const createSession = async () => {
    try {
      setConnectionStatus('connecting');
      
      const result = await videoFeedbackService.createVideoSession({
        video_id: video.id,
        title: `${video.title} -  `,
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
        success('  .');
      }
    } catch (err) {
      setConnectionStatus('disconnected');
      error('  .');
    }
  };

  //  
  const joinSession = async () => {
    if (!session) return;
    
    try {
      setConnectionStatus('connecting');
      
      const result = await videoFeedbackService.joinSession(session.id);
      if (result.success) {
        setConnectionStatus('connected');
        setIsConnected(true);
        success(' .');
      }
    } catch (err) {
      setConnectionStatus('disconnected');
      error('  .');
    }
  };

  //  
  const leaveSession = async () => {
    if (!session) return;
    
    try {
      await videoFeedbackService.leaveSession(session.id);
      onSessionChange?.(null);
      setConnectionStatus('disconnected');
      setIsConnected(false);
      success(' .');
    } catch (err) {
      error('  .');
    }
  };

  //    
  const ConnectionIndicator = () => (
    <div className="flex items-center gap-2">
      {connectionStatus === 'connected' ? (
        <>
          <Wifi size={16} className="text-green-500" />
          <span className="text-sm text-green-600"></span>
        </>
      ) : connectionStatus === 'connecting' ? (
        <>
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500" />
          <span className="text-sm text-blue-600">...</span>
        </>
      ) : (
        <>
          <WifiOff size={16} className="text-gray-400" />
          <span className="text-sm text-gray-500"> </span>
        </>
      )}
    </div>
  );

  //   
  const getRoleIcon = (user: User, isHost: boolean) => {
    if (isHost) return <Crown size={14} className="text-yellow-500" />;
    return <Eye size={14} className="text-gray-400" />;
  };

  //  
  const getUserColor = (userId: number) => {
    const colors = [
      'bg-red-500', 'bg-blue-500', 'bg-green-500', 'bg-yellow-500',
      'bg-purple-500', 'bg-pink-500', 'bg-indigo-500', 'bg-orange-500'
    ];
    return colors[userId % colors.length];
  };

  //    (WebSocket )
  useEffect(() => {
    if (!session || !isConnected) return;

    //  WebSocket     
    const interval = setInterval(() => {
      //    
    }, 5000);

    return () => clearInterval(interval);
  }, [session, isConnected]);

  return (
    <div className={`bg-white border rounded-lg shadow-sm ${className}`}>
      {/*  */}
      <div className="p-4 border-b">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Users size={20} className="text-blue-600" />
            <div>
              <h3 className="font-medium text-gray-800"> </h3>
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

      {/*   */}
      <div className="p-4">
        {!session ? (
          <div className="text-center py-6">
            <Users size={48} className="mx-auto mb-4 text-gray-300" />
            <h4 className="text-lg font-medium text-gray-600 mb-2">  </h4>
            <p className="text-sm text-gray-500 mb-4">
                    .
            </p>
            <Button
              onClick={createSession}
              disabled={connectionStatus === 'connecting'}
              className="bg-blue-600 hover:bg-blue-700 text-white"
            >
              {connectionStatus === 'connecting' ? '...' : '  '}
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            {/*   */}
            <div className="p-3 bg-blue-50 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Activity size={16} className="text-blue-600" />
                <span className="font-medium text-blue-800">{session.title}</span>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">:</span>
                  <span className="ml-2 font-medium">
                    {session.host.first_name} {session.host.last_name}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">:</span>
                  <span className="ml-2 font-medium">{session.participants.length}</span>
                </div>
              </div>
            </div>

            {/*   */}
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600">:</span>
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

            {/*    */}
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
                      {session.playback_state.is_playing ? '' : ''}
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
                    {session.playback_state.playback_rate}x 
                  </span>
                </div>
              </div>
            )}

            {/*   */}
            <div className="flex gap-2">
              {isConnected ? (
                <Button
                  onClick={leaveSession}
                  variant="ghost"
                  className="flex-1 text-red-600 hover:bg-red-50"
                >
                  <UserMinus size={16} className="mr-2" />
                   
                </Button>
              ) : (
                <Button
                  onClick={joinSession}
                  disabled={connectionStatus === 'connecting'}
                  className="flex-1 bg-green-600 hover:bg-green-700 text-white"
                >
                  <UserPlus size={16} className="mr-2" />
                  {connectionStatus === 'connecting' ? '...' : ' '}
                </Button>
              )}
            </div>
          </div>
        )}
      </div>

      {/*   */}
      <Modal
        isOpen={showParticipants}
        onClose={() => setShowParticipants(false)}
        title=" "
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
                        
                      </span>
                    )}
                  </div>
                  <div className="text-sm text-gray-500">{participant.email}</div>
                </div>
                
                <div className="text-xs text-gray-400">
                  {participant.id === currentUser.id ? '' : ''}
                </div>
              </div>
            ))}
          </div>
        )}
      </Modal>

      {/*   */}
      <Modal
        isOpen={showSettings}
        onClose={() => setShowSettings(false)}
        title=" "
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
                <div className="font-medium text-gray-800">  </div>
                <div className="text-sm text-gray-500">    .</div>
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
                <div className="font-medium text-gray-800"> </div>
                <div className="text-sm text-gray-500">    .</div>
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
                <div className="font-medium text-gray-800">    </div>
                <div className="text-sm text-gray-500">     .</div>
              </div>
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
                
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
              
            </Button>
            <Button
              variant="ghost"
              onClick={() => setShowSettings(false)}
              className="px-6"
            >
              
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}