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
  viewer: `${currentUser?.first_name || 'Someone'}   .    .`,
  reviewer: `${currentUser?.first_name || 'Someone'}   .   .`,
  editor: `${currentUser?.first_name || 'Someone'}    .  .`
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

  //  
  const addEmail = () => {
    const email = emailInput.trim().toLowerCase();
    
    if (!email) return;
    
    //   
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      error('   .');
      return;
    }
    
    //  
    if (form.emails.includes(email)) {
      error('  .');
      return;
    }
    
    //   
    if (existingMembers.some(member => member.email === email)) {
      error('   .');
      return;
    }
    
    setForm(prev => ({
      ...prev,
      emails: [...prev.emails, email]
    }));
    setEmailInput('');
  };

  //  
  const removeEmail = (emailToRemove: string) => {
    setForm(prev => ({
      ...prev,
      emails: prev.emails.filter(email => email !== emailToRemove)
    }));
  };

  //      
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

  //  
  const handleSendInvitations = async () => {
    if (form.emails.length === 0) {
      error('  .');
      return;
    }
    
    setIsLoading(true);
    
    try {
      //    
      const invitationResult = await invitationService.sendInvitations({
        emails: form.emails,
        project_id: video.project_id,
        message: form.message,
        role: form.role
      });
      
      if (invitationResult.success) {
        //     (   )
        await videoFeedbackService.inviteToVideo(video.id, form.emails, form.message);
        
        success(`${form.emails.length}  .`);
        onInvitationSent?.(form.emails);
        onClose();
        
        //  
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
        throw new Error(invitationResult.error?.message || '  .');
      }
    } catch (err) {
      console.error('  :', err);
      error('  .');
    } finally {
      setIsLoading(false);
    }
  };

  //   
  const generateShareLink = async () => {
    try {
      //      
      const baseUrl = window.location.origin;
      const shareUrl = `${baseUrl}/video-feedback/${video.id}?invite=true`;
      setShareLink(shareUrl);
    } catch (err) {
      error('   .');
    }
  };

  //  
  const copyShareLink = async () => {
    if (!shareLink) {
      await generateShareLink();
      return;
    }
    
    try {
      await navigator.clipboard.writeText(shareLink);
      setLinkCopied(true);
      success('  .');
      setTimeout(() => setLinkCopied(false), 2000);
    } catch (err) {
      error('  .');
    }
  };

  // Enter   
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
      title=" "
      className="max-w-2xl"
    >
      <div className="space-y-6">
        {/*   */}
        <div className="p-4 bg-gray-50 rounded-lg">
          <h4 className="font-medium text-gray-800 mb-1">{video.title}</h4>
          <p className="text-sm text-gray-600">     .</p>
        </div>

        {/*   */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
              
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
              
            </Button>
          </div>
          
          {/*    */}
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

        {/*   */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
              
          </label>
          
          <div className="grid grid-cols-3 gap-3">
            {[
              { value: 'viewer', label: '', desc: '   ' },
              { value: 'reviewer', label: '', desc: '   ' },
              { value: 'editor', label: '', desc: '  ' }
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

        {/*    */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h5 className="font-medium text-gray-800 mb-3"> </h5>
          <div className="space-y-2">
            {[
              { key: 'canComment', label: '  ' },
              { key: 'canCreateFeedback', label: ' ' },
              { key: 'canResolveFeedback', label: ' /' },
              { key: 'canExport', label: ' ' }
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

        {/*   */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
             
          </label>
          <div className="relative">
            <MessageSquare className="absolute left-3 top-3 text-gray-400" size={16} />
            <textarea
              value={form.message}
              onChange={(e) => setForm(prev => ({ ...prev, message: e.target.value }))}
              rows={4}
              className="w-full pl-9 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
              placeholder="  ..."
            />
          </div>
        </div>

        {/*   */}
        <div className="border-t pt-4">
          <div className="flex items-center justify-between mb-3">
            <label className="text-sm font-medium text-gray-700">
                 
            </label>
            <Button 
              variant="ghost" 
              size="sm"
              onClick={copyShareLink}
              className="flex items-center gap-1"
            >
              {linkCopied ? <Check size={16} /> : <Copy size={16} />}
              {linkCopied ? '' : ' '}
            </Button>
          </div>
          
          {shareLink && (
            <div className="p-3 bg-gray-50 rounded-lg">
              <code className="text-sm text-gray-700 break-all">{shareLink}</code>
            </div>
          )}
        </div>

        {/*    */}
        {existingMembers.length > 0 && (
          <div className="border-t pt-4">
            <h5 className="text-sm font-medium text-gray-700 mb-3 flex items-center gap-2">
              <Users size={16} />
                ({existingMembers.length})
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

        {/*   */}
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
            {form.emails.length > 0 ? `${form.emails.length}  ` : ' '}
          </Button>
          
          <Button
            variant="ghost"
            onClick={onClose}
            className="px-6"
          >
            
          </Button>
        </div>
      </div>
    </Modal>
  );
}