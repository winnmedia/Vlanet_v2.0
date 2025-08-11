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

  //   
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

  //   
  const filteredFriends = friends.filter(friend =>
    friend.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    friend.email.toLowerCase().includes(searchQuery.toLowerCase())
  )

  //  /
  const toggleEmailSelection = (email: string) => {
    setSelectedEmails(prev => 
      prev.includes(email)
        ? prev.filter(e => e !== email)
        : [...prev, email]
    )
  }

  //   
  const addCustomEmail = () => {
    if (!customEmail.trim()) return

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(customEmail)) {
      error('   .')
      return
    }

    if (selectedEmails.includes(customEmail)) {
      error('  .')
      return
    }

    setSelectedEmails(prev => [...prev, customEmail])
    setCustomEmail('')
  }

  //  
  const handleSendInvitations = async () => {
    if (selectedEmails.length === 0) {
      error('  .')
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
        success(`${successCount}  .`)
      }
      if (failCount > 0) {
        error(`${failCount}   .`)
      }

      if (onInviteSent) {
        onInviteSent()
      }

      handleClose()
    } catch (error) {
      console.error('Error sending invitations:', error)
      error('  .')
    } finally {
      setIsLoading(false)
    }
  }

  //    
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
      title={projectTitle ? `${projectTitle} ` : ' '}
      className="max-w-2xl"
    >
      <div className="space-y-6">
        {/*   */}
        {projectTitle && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span className="text-sm font-medium text-blue-800">
                : {projectTitle}
              </span>
            </div>
          </div>
        )}

        {/*   */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
             
          </label>
          <Input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="  ..."
            className="w-full"
          />
        </div>

        {/*   */}
        {filteredFriends.length > 0 && (
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-3">  </h3>
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

        {/*    */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
              
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
              
            </Button>
          </div>
        </div>

        {/*    */}
        {selectedEmails.length > 0 && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
                ({selectedEmails.length})
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

        {/*   */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
              ()
          </label>
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            rows={3}
            placeholder="   !"
          />
        </div>

        {/*  */}
        <div className="flex space-x-3 pt-4">
          <Button
            onClick={handleSendInvitations}
            disabled={isLoading || selectedEmails.length === 0}
            className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg disabled:opacity-50"
          >
            {isLoading ? (
              <div className="flex items-center justify-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span> ...</span>
              </div>
            ) : (
              `  (${selectedEmails.length})`
            )}
          </Button>
          <Button
            onClick={handleClose}
            variant="ghost"
            className="flex-1 border border-gray-300 hover:bg-gray-50 py-2 rounded-lg"
          >
            
          </Button>
        </div>
      </div>
    </Modal>
  )
}

export default InviteModal