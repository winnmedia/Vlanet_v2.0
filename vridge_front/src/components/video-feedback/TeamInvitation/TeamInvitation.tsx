'use client';

import { useState } from 'react';
import { 
  UserPlus, 
  Mail, 
  Users, 
  Copy, 
  Check, 
  Send,
  X,
  AtSign,
  MessageSquare
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Modal } from '@/components/ui/Modal';
import { videoFeedbackService } from '@/lib/api/video-feedback.service';
import { invitationService } from '@/lib/api/invitation.service';
import { useToast } from '@/contexts/toast.context';
import type { User, VideoFile } from '@/types/video-feedback';

interface TeamInvitationProps {
  video: VideoFile;
  currentUser: User;
  existingMembers: User[];
  onInvitationSent?: (emails: string[]) => void;
  isOpen: boolean;
  onClose: () => void;
}

interface InvitationForm {
  emails: string[];
  message: string;
  role: 'viewer' | 'reviewer' | 'editor';
  permissions: {
    canComment: boolean;
    canCreateFeedback: boolean;
    canResolveFeedback: boolean;
    canExport: boolean;
  };
}

const DEFAULT_MESSAGES = {
  viewer: `${currentUser?.first_name || 'Someone'}님이 영상 검토에 초대했습니다. 영상을 확인하고 의견을 남겨주세요.`,
  reviewer: `${currentUser?.first_name || 'Someone'}님이 영상 리뷰에 초대했습니다. 전문적인 피드백을 부탁드립니다.`,
  editor: `${currentUser?.first_name || 'Someone'}님이 영상 편집 협업에 초대했습니다. 함께 작업해주세요.`
};

export default function TeamInvitation({
  video,
  currentUser,
  existingMembers = [],
  onInvitationSent,
  isOpen,
  onClose
}: TeamInvitationProps) {
  const { success, error } = useToast();
  
  const [form, setForm] = useState<InvitationForm>({
    emails: [],
    message: DEFAULT_MESSAGES.reviewer,
    role: 'reviewer',
    permissions: {
      canComment: true,
      canCreateFeedback: true,
      canResolveFeedback: false,
      canExport: false
    }
  });
  
  const [emailInput, setEmailInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [shareLink, setShareLink] = useState('');
  const [linkCopied, setLinkCopied] = useState(false);

  // 이메일 추가
  const addEmail = () => {
    const email = emailInput.trim().toLowerCase();
    
    if (!email) return;
    
    // 이메일 유효성 검증
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      error('올바른 이메일 주소를 입력해주세요.');
      return;
    }
    
    // 중복 체크
    if (form.emails.includes(email)) {
      error('이미 추가된 이메일입니다.');
      return;
    }
    
    // 기존 멤버 체크
    if (existingMembers.some(member => member.email === email)) {
      error('이미 팀에 속한 사용자입니다.');
      return;
    }
    
    setForm(prev => ({
      ...prev,
      emails: [...prev.emails, email]
    }));
    setEmailInput('');
  };

  // 이메일 제거
  const removeEmail = (emailToRemove: string) => {
    setForm(prev => ({
      ...prev,
      emails: prev.emails.filter(email => email !== emailToRemove)
    }));
  };

  // 역할 변경에 따른 권한 자동 설정
  const handleRoleChange = (role: 'viewer' | 'reviewer' | 'editor') => {
    const permissions = {
      viewer: {
        canComment: true,
        canCreateFeedback: false,
        canResolveFeedback: false,
        canExport: false
      },
      reviewer: {
        canComment: true,
        canCreateFeedback: true,
        canResolveFeedback: false,
        canExport: false
      },
      editor: {
        canComment: true,
        canCreateFeedback: true,
        canResolveFeedback: true,
        canExport: true
      }
    };
    
    setForm(prev => ({
      ...prev,
      role,
      message: DEFAULT_MESSAGES[role],
      permissions: permissions[role]
    }));
  };

  // 초대 전송
  const handleSendInvitations = async () => {
    if (form.emails.length === 0) {
      error('초대할 이메일을 추가해주세요.');
      return;
    }
    
    setIsLoading(true);
    
    try {
      // 기존 초대 시스템 사용
      const invitationResult = await invitationService.sendInvitations({
        emails: form.emails,
        project_id: video.project_id,
        message: form.message,
        role: form.role
      });
      
      if (invitationResult.success) {
        // 영상별 초대도 추가로 전송 (영상 피드백 권한 포함)
        await videoFeedbackService.inviteToVideo(video.id, form.emails, form.message);
        
        success(`${form.emails.length}명에게 초대를 전송했습니다.`);
        onInvitationSent?.(form.emails);
        onClose();
        
        // 폼 리셋
        setForm({
          emails: [],
          message: DEFAULT_MESSAGES.reviewer,
          role: 'reviewer',
          permissions: {
            canComment: true,
            canCreateFeedback: true,
            canResolveFeedback: false,
            canExport: false
          }
        });
      } else {
        throw new Error(invitationResult.error?.message || '초대 전송에 실패했습니다.');
      }
    } catch (err) {
      console.error('초대 전송 오류:', err);
      error('초대 전송에 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  // 공유 링크 생성
  const generateShareLink = async () => {
    try {
      // 실제로는 서버에서 공유 토큰을 생성해야 함
      const baseUrl = window.location.origin;
      const shareUrl = `${baseUrl}/video-feedback/${video.id}?invite=true`;
      setShareLink(shareUrl);
    } catch (err) {
      error('공유 링크 생성에 실패했습니다.');
    }
  };

  // 링크 복사
  const copyShareLink = async () => {
    if (!shareLink) {
      await generateShareLink();
      return;
    }
    
    try {
      await navigator.clipboard.writeText(shareLink);
      setLinkCopied(true);
      success('링크가 클립보드에 복사되었습니다.');
      setTimeout(() => setLinkCopied(false), 2000);
    } catch (err) {
      error('링크 복사에 실패했습니다.');
    }
  };

  // Enter 키로 이메일 추가
  const handleEmailKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addEmail();
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="팀원 초대"
      className="max-w-2xl"
    >
      <div className="space-y-6">
        {/* 영상 정보 */}
        <div className="p-4 bg-gray-50 rounded-lg">
          <h4 className="font-medium text-gray-800 mb-1">{video.title}</h4>
          <p className="text-sm text-gray-600">이 영상에 대한 협업 초대를 보냅니다.</p>
        </div>

        {/* 이메일 입력 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            초대할 이메일 주소
          </label>
          
          <div className="flex gap-2">
            <div className="flex-1 relative">
              <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
              <Input
                type="email"
                value={emailInput}
                onChange={(e) => setEmailInput(e.target.value)}
                onKeyDown={handleEmailKeyDown}
                placeholder="email@example.com"
                className="pl-9"
              />
            </div>
            <Button onClick={addEmail} disabled={!emailInput.trim()}>
              추가
            </Button>
          </div>
          
          {/* 추가된 이메일 목록 */}
          {form.emails.length > 0 && (
            <div className="mt-3 space-y-2">
              {form.emails.map((email) => (
                <div key={email} className="flex items-center gap-2 p-2 bg-blue-50 rounded-lg">
                  <AtSign size={14} className="text-blue-600" />
                  <span className="text-sm text-blue-800 flex-1">{email}</span>
                  <button
                    onClick={() => removeEmail(email)}
                    className="text-blue-600 hover:text-red-600 transition-colors"
                  >
                    <X size={14} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* 역할 선택 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            역할 및 권한
          </label>
          
          <div className="grid grid-cols-3 gap-3">
            {[
              { value: 'viewer', label: '뷰어', desc: '영상 시청 및 채팅' },
              { value: 'reviewer', label: '리뷰어', desc: '피드백 작성 및 리뷰' },
              { value: 'editor', label: '에디터', desc: '모든 편집 권한' }
            ].map((role) => (
              <button
                key={role.value}
                onClick={() => handleRoleChange(role.value as any)}
                className={`p-3 border rounded-lg text-left transition-colors ${
                  form.role === role.value
                    ? 'border-blue-500 bg-blue-50 text-blue-700'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
              >
                <div className="font-medium text-sm">{role.label}</div>
                <div className="text-xs text-gray-500 mt-1">{role.desc}</div>
              </button>
            ))}
          </div>
        </div>

        {/* 권한 세부 설정 */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h5 className="font-medium text-gray-800 mb-3">권한 설정</h5>
          <div className="space-y-2">
            {[
              { key: 'canComment', label: '실시간 채팅 참여' },
              { key: 'canCreateFeedback', label: '피드백 작성' },
              { key: 'canResolveFeedback', label: '피드백 해결/관리' },
              { key: 'canExport', label: '리포트 내보내기' }
            ].map((permission) => (
              <label key={permission.key} className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={form.permissions[permission.key as keyof typeof form.permissions]}
                  onChange={(e) => setForm(prev => ({
                    ...prev,
                    permissions: {
                      ...prev.permissions,
                      [permission.key]: e.target.checked
                    }
                  }))}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">{permission.label}</span>
              </label>
            ))}
          </div>
        </div>

        {/* 초대 메시지 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            초대 메시지
          </label>
          <div className="relative">
            <MessageSquare className="absolute left-3 top-3 text-gray-400" size={16} />
            <textarea
              value={form.message}
              onChange={(e) => setForm(prev => ({ ...prev, message: e.target.value }))}
              rows={4}
              className="w-full pl-9 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
              placeholder="초대 메시지를 입력하세요..."
            />
          </div>
        </div>

        {/* 공유 링크 */}
        <div className="border-t pt-4">
          <div className="flex items-center justify-between mb-3">
            <label className="text-sm font-medium text-gray-700">
              또는 공유 링크 사용
            </label>
            <Button 
              variant="ghost" 
              size="sm"
              onClick={copyShareLink}
              className="flex items-center gap-1"
            >
              {linkCopied ? <Check size={16} /> : <Copy size={16} />}
              {linkCopied ? '복사됨' : '링크 복사'}
            </Button>
          </div>
          
          {shareLink && (
            <div className="p-3 bg-gray-50 rounded-lg">
              <code className="text-sm text-gray-700 break-all">{shareLink}</code>
            </div>
          )}
        </div>

        {/* 기존 팀원 표시 */}
        {existingMembers.length > 0 && (
          <div className="border-t pt-4">
            <h5 className="text-sm font-medium text-gray-700 mb-3 flex items-center gap-2">
              <Users size={16} />
              현재 팀원 ({existingMembers.length}명)
            </h5>
            <div className="space-y-2">
              {existingMembers.map((member) => (
                <div key={member.id} className="flex items-center gap-3 p-2 bg-green-50 rounded-lg">
                  <div className="w-6 h-6 bg-green-500 text-white rounded-full flex items-center justify-center text-xs font-bold">
                    {member.first_name[0]}{member.last_name[0]}
                  </div>
                  <div className="flex-1">
                    <div className="text-sm font-medium text-green-800">
                      {member.first_name} {member.last_name}
                    </div>
                    <div className="text-xs text-green-600">{member.email}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 액션 버튼 */}
        <div className="flex gap-3 pt-4 border-t">
          <Button
            onClick={handleSendInvitations}
            disabled={form.emails.length === 0 || isLoading}
            className="flex-1 bg-blue-600 hover:bg-blue-700 text-white flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            ) : (
              <Send size={16} />
            )}
            {form.emails.length > 0 ? `${form.emails.length}명에게 초대 전송` : '초대 전송'}
          </Button>
          
          <Button
            variant="ghost"
            onClick={onClose}
            className="px-6"
          >
            취소
          </Button>
        </div>
      </div>
    </Modal>
  );
}