'use client'

import { useState, useEffect } from 'react'
import { Modal } from '@/components/ui/Modal'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { useToast } from '@/contexts/toast.context'
import { invitationService, type SendInvitationData, type Friend } from '@/lib/api/invitation.service'

export interface InviteModalProps {
  isOpen: boolean
  onClose: () => void
  projectId?: number
  projectTitle?: string
  onInviteSent?: () => void
}

const InviteModal = ({ 
  isOpen, 
  onClose, 
  projectId, 
  projectTitle,
  onInviteSent 
}: InviteModalProps) => {
  const { success, error } = useToast()
  const [isLoading, setIsLoading] = useState(false)
  const [friends, setFriends] = useState<Friend[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedEmails, setSelectedEmails] = useState<string[]>([])
  const [customEmail, setCustomEmail] = useState('')
  const [message, setMessage] = useState('')

  // 친구 목록 로드
  const loadFriends = async () => {
    try {
      const result = await invitationService.getFriends()
      if (result.success && result.data) {
        setFriends(result.data)
      }
    } catch (error) {
      console.error('Error loading friends:', error)
    }
  }

  useEffect(() => {
    if (isOpen) {
      loadFriends()
    }
  }, [isOpen])

  // 친구 목록 필터링
  const filteredFriends = friends.filter(friend =>
    friend.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    friend.email.toLowerCase().includes(searchQuery.toLowerCase())
  )

  // 이메일 선택/해제
  const toggleEmailSelection = (email: string) => {
    setSelectedEmails(prev => 
      prev.includes(email)
        ? prev.filter(e => e !== email)
        : [...prev, email]
    )
  }

  // 커스텀 이메일 추가
  const addCustomEmail = () => {
    if (!customEmail.trim()) return

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(customEmail)) {
      error('올바른 이메일 형식이 아닙니다.')
      return
    }

    if (selectedEmails.includes(customEmail)) {
      error('이미 선택된 이메일입니다.')
      return
    }

    setSelectedEmails(prev => [...prev, customEmail])
    setCustomEmail('')
  }

  // 초대장 발송
  const handleSendInvitations = async () => {
    if (selectedEmails.length === 0) {
      error('초대할 이메일을 선택해주세요.')
      return
    }

    setIsLoading(true)
    try {
      const promises = selectedEmails.map(email => {
        const invitationData: SendInvitationData = {
          recipient_email: email,
          project_id: projectId,
          message: message.trim() || undefined
        }
        return invitationService.sendInvitation(invitationData)
      })

      const results = await Promise.all(promises)
      const successCount = results.filter(result => result.success).length
      const failCount = results.length - successCount

      if (successCount > 0) {
        success(`${successCount}명에게 초대장을 발송했습니다.`)
      }
      if (failCount > 0) {
        error(`${failCount}명에게 초대장 발송에 실패했습니다.`)
      }

      if (onInviteSent) {
        onInviteSent()
      }

      handleClose()
    } catch (error) {
      console.error('Error sending invitations:', error)
      error('초대장 발송에 실패했습니다.')
    } finally {
      setIsLoading(false)
    }
  }

  // 모달 닫기 및 초기화
  const handleClose = () => {
    setSelectedEmails([])
    setCustomEmail('')
    setMessage('')
    setSearchQuery('')
    onClose()
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title={projectTitle ? `${projectTitle}에 초대하기` : '팀원 초대하기'}
      className="max-w-2xl"
    >
      <div className="space-y-6">
        {/* 프로젝트 정보 */}
        {projectTitle && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span className="text-sm font-medium text-blue-800">
                프로젝트: {projectTitle}
              </span>
            </div>
          </div>
        )}

        {/* 이메일 검색 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            팀원 검색
          </label>
          <Input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="이름이나 이메일로 검색..."
            className="w-full"
          />
        </div>

        {/* 친구 목록 */}
        {filteredFriends.length > 0 && (
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-3">최근 협업한 팀원</h3>
            <div className="max-h-40 overflow-y-auto border border-gray-200 rounded-lg">
              {filteredFriends.map((friend) => (
                <div
                  key={friend.id}
                  className={`p-3 border-b border-gray-100 last:border-b-0 cursor-pointer hover:bg-gray-50 ${
                    selectedEmails.includes(friend.email) ? 'bg-blue-50 border-blue-200' : ''
                  }`}
                  onClick={() => toggleEmailSelection(friend.email)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
                        {friend.avatar ? (
                          <img src={friend.avatar} alt={friend.name} className="w-8 h-8 rounded-full" />
                        ) : (
                          <span className="text-sm font-medium text-gray-600">
                            {friend.name.charAt(0).toUpperCase()}
                          </span>
                        )}
                      </div>
                      <div>
                        <div className="text-sm font-medium text-gray-900">{friend.name}</div>
                        <div className="text-xs text-gray-500">{friend.email}</div>
                      </div>
                    </div>
                    <div className={`w-4 h-4 rounded border-2 ${
                      selectedEmails.includes(friend.email)
                        ? 'bg-blue-500 border-blue-500'
                        : 'border-gray-300'
                    }`}>
                      {selectedEmails.includes(friend.email) && (
                        <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 새 이메일 추가 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            새 이메일 추가
          </label>
          <div className="flex space-x-2">
            <Input
              type="email"
              value={customEmail}
              onChange={(e) => setCustomEmail(e.target.value)}
              placeholder="example@email.com"
              className="flex-1"
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault()
                  addCustomEmail()
                }
              }}
            />
            <Button
              onClick={addCustomEmail}
              variant="ghost"
              className="border border-gray-300 hover:bg-gray-50"
            >
              추가
            </Button>
          </div>
        </div>

        {/* 선택된 이메일 목록 */}
        {selectedEmails.length > 0 && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              선택된 이메일 ({selectedEmails.length}명)
            </label>
            <div className="flex flex-wrap gap-2">
              {selectedEmails.map((email) => (
                <div
                  key={email}
                  className="flex items-center space-x-2 bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm"
                >
                  <span>{email}</span>
                  <button
                    onClick={() => toggleEmailSelection(email)}
                    className="text-blue-600 hover:text-blue-800"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 초대 메시지 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            초대 메시지 (선택사항)
          </label>
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            rows={3}
            placeholder="함께 작업하고 싶어서 초대드립니다!"
          />
        </div>

        {/* 버튼 */}
        <div className="flex space-x-3 pt-4">
          <Button
            onClick={handleSendInvitations}
            disabled={isLoading || selectedEmails.length === 0}
            className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg disabled:opacity-50"
          >
            {isLoading ? (
              <div className="flex items-center justify-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>발송 중...</span>
              </div>
            ) : (
              `초대장 발송 (${selectedEmails.length}명)`
            )}
          </Button>
          <Button
            onClick={handleClose}
            variant="ghost"
            className="flex-1 border border-gray-300 hover:bg-gray-50 py-2 rounded-lg"
          >
            취소
          </Button>
        </div>
      </div>
    </Modal>
  )
}

export default InviteModal