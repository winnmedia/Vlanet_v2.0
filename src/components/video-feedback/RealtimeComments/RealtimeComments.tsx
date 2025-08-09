'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { 
  Send, 
  Smile, 
  AtSign, 
  Clock, 
  Users, 
  MessageCircle,
  Pin,
  Trash2,
  Copy,
  MoreHorizontal
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import type { 
  RealtimeComment, 
  User, 
  VideoSession,
  CreateRealtimeCommentData 
} from '@/types/video-feedback';

interface RealtimeCommentsProps {
  session: VideoSession;
  comments: RealtimeComment[];
  currentUser: User;
  currentTime?: number;
  onSendComment?: (data: CreateRealtimeCommentData) => void;
  onDeleteComment?: (commentId: string) => void;
  onMentionUser?: (userId: number) => void;
  className?: string;
}

interface CommentInputState {
  content: string;
  mentions: number[];
  isTimestampComment: boolean;
  timestamp?: number;
}

export default function RealtimeComments({
  session,
  comments,
  currentUser,
  currentTime = 0,
  onSendComment,
  onDeleteComment,
  onMentionUser,
  className = ''
}: RealtimeCommentsProps) {
  const [inputState, setInputState] = useState<CommentInputState>({
    content: '',
    mentions: [],
    isTimestampComment: false
  });

  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const [showMentionDropdown, setShowMentionDropdown] = useState(false);
  const [mentionQuery, setMentionQuery] = useState('');
  const [pinnedComments, setPinnedComments] = useState<Set<string>>(new Set());

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const mentionDropdownRef = useRef<HTMLDivElement>(null);

  // 자동 스크롤
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [comments]);

  // 멘션 가능한 사용자 필터링
  const filteredMentionUsers = session.participants.filter(user => {
    if (!mentionQuery) return true;
    const fullName = `${user.first_name} ${user.last_name}`.toLowerCase();
    return fullName.includes(mentionQuery.toLowerCase()) || 
           user.email.toLowerCase().includes(mentionQuery.toLowerCase());
  });

  // 시간 포맷팅
  const formatTime = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  // 상대 시간 포맷팅
  const formatRelativeTime = (dateString: string): string => {
    const now = new Date();
    const commentTime = new Date(dateString);
    const diff = now.getTime() - commentTime.getTime();
    
    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (minutes < 1) return '방금 전';
    if (minutes < 60) return `${minutes}분 전`;
    if (hours < 24) return `${hours}시간 전`;
    return `${days}일 전`;
  };

  // 멘션 처리
  const handleMentionClick = (user: User) => {
    const currentContent = inputState.content;
    const atIndex = currentContent.lastIndexOf('@');
    const beforeMention = currentContent.substring(0, atIndex);
    const afterMention = currentContent.substring(atIndex + mentionQuery.length + 1);
    
    const newContent = `${beforeMention}@${user.first_name}${user.last_name} ${afterMention}`;
    const newMentions = [...inputState.mentions, user.id];
    
    setInputState(prev => ({
      ...prev,
      content: newContent,
      mentions: newMentions
    }));
    
    setShowMentionDropdown(false);
    setMentionQuery('');
    inputRef.current?.focus();
  };

  // 입력 변경 처리
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setInputState(prev => ({ ...prev, content: value }));
    
    // 멘션 감지
    const atIndex = value.lastIndexOf('@');
    if (atIndex !== -1 && atIndex === value.length - 1) {
      setShowMentionDropdown(true);
      setMentionQuery('');
    } else if (atIndex !== -1) {
      const afterAt = value.substring(atIndex + 1);
      if (!afterAt.includes(' ') && afterAt.length > 0) {
        setMentionQuery(afterAt);
        setShowMentionDropdown(true);
      } else {
        setShowMentionDropdown(false);
      }
    } else {
      setShowMentionDropdown(false);
    }
  };

  // 코멘트 전송
  const handleSendComment = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!inputState.content.trim()) return;
    
    const commentData: CreateRealtimeCommentData = {
      session_id: session.id,
      content: inputState.content.trim(),
      mentions: inputState.mentions,
      type: inputState.isTimestampComment ? 'timestamp' : 'chat',
      ...(inputState.isTimestampComment && { timestamp: inputState.timestamp || currentTime })
    };
    
    onSendComment?.(commentData);
    
    // 입력 상태 리셋
    setInputState({
      content: '',
      mentions: [],
      isTimestampComment: false
    });
  };

  // 타임스탬프 코멘트 토글
  const toggleTimestampComment = () => {
    setInputState(prev => ({
      ...prev,
      isTimestampComment: !prev.isTimestampComment,
      timestamp: prev.isTimestampComment ? undefined : currentTime
    }));
  };

  // 코멘트 고정
  const togglePinComment = (commentId: string) => {
    setPinnedComments(prev => {
      const newSet = new Set(prev);
      if (newSet.has(commentId)) {
        newSet.delete(commentId);
      } else {
        newSet.add(commentId);
      }
      return newSet;
    });
  };

  // 키보드 단축키
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendComment(e as any);
    } else if (e.key === 'Escape') {
      setShowMentionDropdown(false);
      setShowEmojiPicker(false);
    } else if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
      if (showMentionDropdown && filteredMentionUsers.length > 0) {
        e.preventDefault();
        // 멘션 드롭다운 네비게이션 (구현 생략)
      }
    }
  };

  // 정렬된 코멘트 (고정된 것들을 위에 표시)
  const sortedComments = [...comments].sort((a, b) => {
    const aIsPinned = pinnedComments.has(a.id);
    const bIsPinned = pinnedComments.has(b.id);
    
    if (aIsPinned && !bIsPinned) return -1;
    if (!aIsPinned && bIsPinned) return 1;
    
    return new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
  });

  // 사용자별 아바타 색상
  const getUserColor = (userId: number): string => {
    const colors = [
      'bg-red-500', 'bg-blue-500', 'bg-green-500', 'bg-yellow-500',
      'bg-purple-500', 'bg-pink-500', 'bg-indigo-500', 'bg-orange-500'
    ];
    return colors[userId % colors.length];
  };

  return (
    <div className={`flex flex-col h-full bg-white ${className}`}>
      {/* 헤더 */}
      <div className="flex items-center justify-between p-4 border-b">
        <div className="flex items-center gap-2">
          <MessageCircle size={20} className="text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-800">실시간 채팅</h3>
          <div className="flex items-center gap-1 text-sm text-gray-500">
            <Users size={16} />
            {session.participants.length}명 참여중
          </div>
        </div>
      </div>

      {/* 메시지 영역 */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {sortedComments.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <MessageCircle size={48} className="mb-4 opacity-50" />
            <p className="text-lg font-medium">아직 메시지가 없습니다</p>
            <p className="text-sm">첫 번째 메시지를 보내보세요!</p>
          </div>
        ) : (
          <>
            {sortedComments.map((comment) => (
              <div 
                key={comment.id} 
                className={`flex gap-3 group ${pinnedComments.has(comment.id) ? 'bg-yellow-50 p-2 rounded-lg border border-yellow-200' : ''}`}
              >
                {/* 아바타 */}
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-bold flex-shrink-0 ${getUserColor(comment.author.id)}`}>
                  {comment.author.first_name[0]}{comment.author.last_name[0]}
                </div>

                {/* 메시지 내용 */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-medium text-gray-900 text-sm">
                      {comment.author.first_name} {comment.author.last_name}
                    </span>
                    
                    {comment.type === 'timestamp' && comment.timestamp !== undefined && (
                      <div className="flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs">
                        <Clock size={12} />
                        {formatTime(comment.timestamp)}
                      </div>
                    )}
                    
                    <span className="text-xs text-gray-500">
                      {formatRelativeTime(comment.created_at)}
                    </span>

                    {pinnedComments.has(comment.id) && (
                      <Pin size={12} className="text-yellow-600" />
                    )}
                  </div>
                  
                  <p className="text-gray-700 text-sm break-words">{comment.content}</p>

                  {/* 메시지 액션 */}
                  <div className="opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-2 mt-2">
                    {currentUser.id === comment.author.id && (
                      <button
                        onClick={() => onDeleteComment?.(comment.id)}
                        className="text-xs text-red-600 hover:text-red-700 flex items-center gap-1"
                      >
                        <Trash2 size={12} />
                        삭제
                      </button>
                    )}
                    
                    <button
                      onClick={() => togglePinComment(comment.id)}
                      className={`text-xs flex items-center gap-1 ${
                        pinnedComments.has(comment.id) 
                          ? 'text-yellow-600 hover:text-yellow-700' 
                          : 'text-gray-600 hover:text-gray-700'
                      }`}
                    >
                      <Pin size={12} />
                      {pinnedComments.has(comment.id) ? '고정 해제' : '고정'}
                    </button>
                    
                    <button
                      onClick={() => navigator.clipboard.writeText(comment.content)}
                      className="text-xs text-gray-600 hover:text-gray-700 flex items-center gap-1"
                    >
                      <Copy size={12} />
                      복사
                    </button>
                  </div>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* 입력 영역 */}
      <div className="p-4 border-t relative">
        {/* 멘션 드롭다운 */}
        {showMentionDropdown && (
          <div 
            ref={mentionDropdownRef}
            className="absolute bottom-full left-4 right-4 mb-2 bg-white border border-gray-300 rounded-lg shadow-lg max-h-40 overflow-y-auto z-10"
          >
            {filteredMentionUsers.length === 0 ? (
              <div className="p-3 text-sm text-gray-500">멘션할 사용자가 없습니다</div>
            ) : (
              filteredMentionUsers.map(user => (
                <button
                  key={user.id}
                  onClick={() => handleMentionClick(user)}
                  className="w-full flex items-center gap-3 p-3 hover:bg-gray-50 text-left"
                >
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center text-white text-xs font-bold ${getUserColor(user.id)}`}>
                    {user.first_name[0]}{user.last_name[0]}
                  </div>
                  <div>
                    <div className="text-sm font-medium">{user.first_name} {user.last_name}</div>
                    <div className="text-xs text-gray-500">{user.email}</div>
                  </div>
                </button>
              ))
            )}
          </div>
        )}

        {/* 타임스탬프 코멘트 모드 표시 */}
        {inputState.isTimestampComment && (
          <div className="flex items-center gap-2 mb-2 p-2 bg-blue-50 rounded-lg">
            <Clock size={16} className="text-blue-600" />
            <span className="text-sm text-blue-700">
              {formatTime(inputState.timestamp || currentTime)} 시점에 코멘트 작성중
            </span>
            <button
              onClick={toggleTimestampComment}
              className="text-xs text-blue-600 hover:text-blue-700 ml-auto"
            >
              취소
            </button>
          </div>
        )}

        {/* 입력 폼 */}
        <form onSubmit={handleSendComment} className="flex gap-2">
          <div className="flex-1 relative">
            <input
              ref={inputRef}
              type="text"
              value={inputState.content}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              placeholder="메시지를 입력하세요... (@를 입력해서 멘션)"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 pr-20"
            />
            
            {/* 입력 액션 버튼들 */}
            <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex items-center gap-1">
              <button
                type="button"
                onClick={() => {
                  const input = inputRef.current;
                  if (input) {
                    input.value += '@';
                    handleInputChange({ target: input } as React.ChangeEvent<HTMLInputElement>);
                    input.focus();
                  }
                }}
                className="p-1 text-gray-400 hover:text-blue-600 transition-colors"
                title="멘션"
              >
                <AtSign size={16} />
              </button>
              
              <button
                type="button"
                onClick={toggleTimestampComment}
                className={`p-1 transition-colors ${
                  inputState.isTimestampComment 
                    ? 'text-blue-600' 
                    : 'text-gray-400 hover:text-blue-600'
                }`}
                title="현재 시점에 코멘트"
              >
                <Clock size={16} />
              </button>
            </div>
          </div>

          <Button
            type="submit"
            disabled={!inputState.content.trim()}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 flex items-center gap-2"
          >
            <Send size={16} />
            전송
          </Button>
        </form>

        {/* 입력 도움말 */}
        <div className="flex justify-between items-center mt-2 text-xs text-gray-500">
          <div className="flex items-center gap-4">
            <span>Enter: 전송</span>
            <span>@: 멘션</span>
            <span>Esc: 취소</span>
          </div>
          <div>
            {session.participants.length}명이 함께 보고 있습니다
          </div>
        </div>
      </div>
    </div>
  );
}