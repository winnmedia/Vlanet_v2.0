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

  //   
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
      error('  .')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadInvitations()
  }, [type])

  //   (/)
  const handleResponse = async (invitationId: number, response: 'accepted' | 'declined') => {
    if (processingIds.has(invitationId)) return

    setProcessingIds(prev => new Set([...prev, invitationId]))
    try {
      const result = await invitationService.respondToInvitation(invitationId, {
        status: response
      })

      if (result.success) {
        success(response === 'accepted' ? ' .' : ' .')
        await loadInvitations()
        if (onInvitationUpdate) {
          onInvitationUpdate()
        }
      } else {
        throw new Error(result.error?.message || 'Failed to respond to invitation')
      }
    } catch (error) {
      console.error('Error responding to invitation:', error)
      error('  .')
    } finally {
      setProcessingIds(prev => {
        const newSet = new Set(prev)
        newSet.delete(invitationId)
        return newSet
      })
    }
  }

  //  
  const handleCancel = async (invitationId: number) => {
    if (processingIds.has(invitationId)) return

    if (!window.confirm(' ?')) return

    setProcessingIds(prev => new Set([...prev, invitationId]))
    try {
      const result = await invitationService.cancelInvitation(invitationId)

      if (result.success) {
        success(' .')
        await loadInvitations()
        if (onInvitationUpdate) {
          onInvitationUpdate()
        }
      } else {
        throw new Error(result.error?.message || 'Failed to cancel invitation')
      }
    } catch (error) {
      console.error('Error cancelling invitation:', error)
      error('  .')
    } finally {
      setProcessingIds(prev => {
        const newSet = new Set(prev)
        newSet.delete(invitationId)
        return newSet
      })
    }
  }

  //  
  const handleResend = async (invitationId: number) => {
    if (processingIds.has(invitationId)) return

    setProcessingIds(prev => new Set([...prev, invitationId]))
    try {
      const result = await invitationService.resendInvitation(invitationId)

      if (result.success) {
        success(' .')
        await loadInvitations()
      } else {
        throw new Error(result.error?.message || 'Failed to resend invitation')
      }
    } catch (error) {
      console.error('Error resending invitation:', error)
      error('  .')
    } finally {
      setProcessingIds(prev => {
        const newSet = new Set(prev)
        newSet.delete(invitationId)
        return newSet
      })
    }
  }

  //    
  const getStatusInfo = (invitation: Invitation) => {
    const isExpired = new Date(invitation.expires_at) < new Date()
    
    switch (invitation.status) {
      case 'pending':
        if (isExpired) {
          return {
            text: '',
            className: 'bg-gray-100 text-gray-600',
            canRespond: false,
            canCancel: false,
            canResend: type === 'sent'
          }
        }
        return {
          text: '',
          className: 'bg-yellow-100 text-yellow-800',
          canRespond: type === 'received',
          canCancel: type === 'sent',
          canResend: false
        }
      case 'accepted':
        return {
          text: '',
          className: 'bg-green-100 text-green-800',
          canRespond: false,
          canCancel: false,
          canResend: false
        }
      case 'declined':
        return {
          text: '',
          className: 'bg-red-100 text-red-800',
          canRespond: false,
          canCancel: false,
          canResend: type === 'sent'
        }
      case 'cancelled':
        return {
          text: '',
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
        {type === 'received' ? '  .' : '  .'}
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
                          <span className="text-sm text-gray-500 ml-2"> </span>
                        </>
                      ) : (
                        invitation.recipient_email
                      )}
                    </div>
                    <div className="text-sm text-gray-500">
                      {invitation.project_title || ' '}
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
                    : {formatDistanceToNow(new Date(invitation.expires_at), { 
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

                {/*   */}
                <div className="flex space-x-2">
                  {statusInfo.canRespond && (
                    <>
                      <Button
                        onClick={() => handleResponse(invitation.id, 'accepted')}
                        disabled={isProcessing}
                        className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 text-sm"
                      >
                        
                      </Button>
                      <Button
                        onClick={() => handleResponse(invitation.id, 'declined')}
                        disabled={isProcessing}
                        variant="ghost"
                        className="border border-gray-300 hover:bg-gray-50 px-3 py-1 text-sm"
                      >
                        
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
                      
                    </Button>
                  )}

                  {statusInfo.canResend && (
                    <Button
                      onClick={() => handleResend(invitation.id)}
                      disabled={isProcessing}
                      variant="ghost"
                      className="text-blue-600 hover:bg-blue-50 px-3 py-1 text-sm"
                    >
                      
                    </Button>
                  )}
                </div>
              </div>
            </div>

            {isProcessing && (
              <div className="mt-3 flex items-center space-x-2 text-sm text-gray-500">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-400"></div>
                <span> ...</span>
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}

export default InvitationList