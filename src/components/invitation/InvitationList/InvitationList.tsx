'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/Button'
import { useToast } from '@/contexts/toast.context'
import { invitationService, type Invitation } from '@/lib/api/invitation.service'
import { formatDistanceToNow, isAfter } from 'date-fns'
import { ko } from 'date-fns/locale'

export interface InvitationListProps {
  type: 'received' | 'sent'
  onInvitationUpdate?: () => void
}

const InvitationList = ({ type, onInvitationUpdate }: InvitationListProps) => {
  const { success, error } = useToast()
  const [invitations, setInvitations] = useState<Invitation[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [processingIds, setProcessingIds] = useState<Set<number>>(new Set())

  // 초대장 목록 로드
  const loadInvitations = async () => {
    try {
      const result = type === 'received' 
        ? await invitationService.getReceivedInvitations()
        : await invitationService.getSentInvitations()

      if (result.success && result.data) {
        setInvitations(result.data)
      } else {
        throw new Error(result.error?.message || 'Failed to load invitations')
      }
    } catch (error) {
      console.error('Error loading invitations:', error)
      error('초대장을 불러오는데 실패했습니다.')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadInvitations()
  }, [type])

  // 초대장 응답 (수락/거절)
  const handleResponse = async (invitationId: number, response: 'accepted' | 'declined') => {
    if (processingIds.has(invitationId)) return

    setProcessingIds(prev => new Set([...prev, invitationId]))
    try {
      const result = await invitationService.respondToInvitation(invitationId, {
        status: response
      })

      if (result.success) {
        success(response === 'accepted' ? '초대를 수락했습니다.' : '초대를 거절했습니다.')
        await loadInvitations()
        if (onInvitationUpdate) {
          onInvitationUpdate()
        }
      } else {
        throw new Error(result.error?.message || 'Failed to respond to invitation')
      }
    } catch (error) {
      console.error('Error responding to invitation:', error)
      error('초대 응답에 실패했습니다.')
    } finally {
      setProcessingIds(prev => {
        const newSet = new Set(prev)
        newSet.delete(invitationId)
        return newSet
      })
    }
  }

  // 초대장 취소
  const handleCancel = async (invitationId: number) => {
    if (processingIds.has(invitationId)) return

    if (!window.confirm('초대를 취소하시겠습니까?')) return

    setProcessingIds(prev => new Set([...prev, invitationId]))
    try {
      const result = await invitationService.cancelInvitation(invitationId)

      if (result.success) {
        success('초대를 취소했습니다.')
        await loadInvitations()
        if (onInvitationUpdate) {
          onInvitationUpdate()
        }
      } else {
        throw new Error(result.error?.message || 'Failed to cancel invitation')
      }
    } catch (error) {
      console.error('Error cancelling invitation:', error)
      error('초대 취소에 실패했습니다.')
    } finally {
      setProcessingIds(prev => {
        const newSet = new Set(prev)
        newSet.delete(invitationId)
        return newSet
      })
    }
  }

  // 초대장 재발송
  const handleResend = async (invitationId: number) => {
    if (processingIds.has(invitationId)) return

    setProcessingIds(prev => new Set([...prev, invitationId]))
    try {
      const result = await invitationService.resendInvitation(invitationId)

      if (result.success) {
        success('초대장을 재발송했습니다.')
        await loadInvitations()
      } else {
        throw new Error(result.error?.message || 'Failed to resend invitation')
      }
    } catch (error) {
      console.error('Error resending invitation:', error)
      error('초대장 재발송에 실패했습니다.')
    } finally {
      setProcessingIds(prev => {
        const newSet = new Set(prev)
        newSet.delete(invitationId)
        return newSet
      })
    }
  }

  // 상태별 스타일 및 텍스트
  const getStatusInfo = (invitation: Invitation) => {
    const isExpired = new Date(invitation.expires_at) < new Date()
    
    switch (invitation.status) {
      case 'pending':
        if (isExpired) {
          return {
            text: '만료됨',
            className: 'bg-gray-100 text-gray-600',
            canRespond: false,
            canCancel: false,
            canResend: type === 'sent'
          }
        }
        return {
          text: '대기중',
          className: 'bg-yellow-100 text-yellow-800',
          canRespond: type === 'received',
          canCancel: type === 'sent',
          canResend: false
        }
      case 'accepted':
        return {
          text: '수락됨',
          className: 'bg-green-100 text-green-800',
          canRespond: false,
          canCancel: false,
          canResend: false
        }
      case 'declined':
        return {
          text: '거절됨',
          className: 'bg-red-100 text-red-800',
          canRespond: false,
          canCancel: false,
          canResend: type === 'sent'
        }
      case 'cancelled':
        return {
          text: '취소됨',
          className: 'bg-gray-100 text-gray-600',
          canRespond: false,
          canCancel: false,
          canResend: false
        }
      default:
        return {
          text: invitation.status,
          className: 'bg-gray-100 text-gray-600',
          canRespond: false,
          canCancel: false,
          canResend: false
        }
    }
  }

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-32">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (invitations.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        {type === 'received' ? '받은 초대가 없습니다.' : '보낸 초대가 없습니다.'}
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {invitations.map((invitation) => {
        const statusInfo = getStatusInfo(invitation)
        const isProcessing = processingIds.has(invitation.id)
        
        return (
          <div key={invitation.id} className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-2">
                  <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
                    <span className="text-sm font-medium text-gray-600">
                      {type === 'received' 
                        ? invitation.sender_name?.charAt(0).toUpperCase() || invitation.sender_email.charAt(0).toUpperCase()
                        : invitation.recipient_email.charAt(0).toUpperCase()
                      }
                    </span>
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">
                      {type === 'received' ? (
                        <>
                          <span>{invitation.sender_name || invitation.sender_email}</span>
                          <span className="text-sm text-gray-500 ml-2">님이 초대했습니다</span>
                        </>
                      ) : (
                        invitation.recipient_email
                      )}
                    </div>
                    <div className="text-sm text-gray-500">
                      {invitation.project_title || '일반 초대'}
                    </div>
                  </div>
                </div>

                {invitation.message && (
                  <div className="bg-gray-50 border border-gray-200 rounded p-3 mb-3">
                    <div className="text-sm text-gray-700">{invitation.message}</div>
                  </div>
                )}

                <div className="flex items-center space-x-4 text-xs text-gray-500">
                  <span>
                    {formatDistanceToNow(new Date(invitation.created_at), { 
                      addSuffix: true, 
                      locale: ko 
                    })}
                  </span>
                  <span>•</span>
                  <span>
                    만료: {formatDistanceToNow(new Date(invitation.expires_at), { 
                      addSuffix: true, 
                      locale: ko 
                    })}
                  </span>
                </div>
              </div>

              <div className="flex items-center space-x-3">
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${statusInfo.className}`}>
                  {statusInfo.text}
                </span>

                {/* 액션 버튼들 */}
                <div className="flex space-x-2">
                  {statusInfo.canRespond && (
                    <>
                      <Button
                        onClick={() => handleResponse(invitation.id, 'accepted')}
                        disabled={isProcessing}
                        className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 text-sm"
                      >
                        수락
                      </Button>
                      <Button
                        onClick={() => handleResponse(invitation.id, 'declined')}
                        disabled={isProcessing}
                        variant="ghost"
                        className="border border-gray-300 hover:bg-gray-50 px-3 py-1 text-sm"
                      >
                        거절
                      </Button>
                    </>
                  )}

                  {statusInfo.canCancel && (
                    <Button
                      onClick={() => handleCancel(invitation.id)}
                      disabled={isProcessing}
                      variant="ghost"
                      className="text-red-600 hover:bg-red-50 px-3 py-1 text-sm"
                    >
                      취소
                    </Button>
                  )}

                  {statusInfo.canResend && (
                    <Button
                      onClick={() => handleResend(invitation.id)}
                      disabled={isProcessing}
                      variant="ghost"
                      className="text-blue-600 hover:bg-blue-50 px-3 py-1 text-sm"
                    >
                      재발송
                    </Button>
                  )}
                </div>
              </div>
            </div>

            {isProcessing && (
              <div className="mt-3 flex items-center space-x-2 text-sm text-gray-500">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-400"></div>
                <span>처리 중...</span>
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}

export default InvitationList