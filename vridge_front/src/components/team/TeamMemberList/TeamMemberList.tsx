'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { useToast } from '@/contexts/toast.context'
import { invitationService, type TeamMember, type Friend } from '@/lib/api/invitation.service'
import { formatDistanceToNow } from 'date-fns'
import { ko } from 'date-fns/locale'

export interface TeamMemberListProps {
  projectId?: number
  onInviteClick?: () => void
}

const TeamMemberList = ({ projectId, onInviteClick }: TeamMemberListProps) => {
  const { success, error } = useToast()
  const [activeTab, setActiveTab] = useState<'members' | 'friends'>('members')
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([])
  const [friends, setFriends] = useState<Friend[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [removingIds, setRemovingIds] = useState<Set<number>>(new Set())

  //   
  const loadTeamMembers = async () => {
    try {
      const result = await invitationService.getTeamMembers(projectId)
      if (result.success && result.data) {
        setTeamMembers(result.data)
      }
    } catch (error) {
      console.error('Error loading team members:', error)
      error('   .')
    }
  }

  //   
  const loadFriends = async () => {
    try {
      const result = await invitationService.getFriends()
      if (result.success && result.data) {
        setFriends(result.data)
      }
    } catch (error) {
      console.error('Error loading friends:', error)
      error('   .')
    }
  }

  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true)
      try {
        if (activeTab === 'members') {
          await loadTeamMembers()
        } else {
          await loadFriends()
        }
      } finally {
        setIsLoading(false)
      }
    }

    loadData()
  }, [activeTab, projectId])

  //  
  const handleRemoveTeamMember = async (memberId: number) => {
    if (removingIds.has(memberId)) return

    if (!window.confirm('   ?')) return

    setRemovingIds(prev => new Set([...prev, memberId]))
    try {
      const result = await invitationService.removeTeamMember(memberId, projectId)
      if (result.success) {
        success(' .')
        await loadTeamMembers()
      } else {
        throw new Error(result.error?.message || 'Failed to remove team member')
      }
    } catch (error) {
      console.error('Error removing team member:', error)
      error('  .')
    } finally {
      setRemovingIds(prev => {
        const newSet = new Set(prev)
        newSet.delete(memberId)
        return newSet
      })
    }
  }

  //  
  const handleRemoveFriend = async (friendId: number) => {
    if (removingIds.has(friendId)) return

    if (!window.confirm('   ?')) return

    setRemovingIds(prev => new Set([...prev, friendId]))
    try {
      const result = await invitationService.removeFriend(friendId)
      if (result.success) {
        success(' .')
        await loadFriends()
      } else {
        throw new Error(result.error?.message || 'Failed to remove friend')
      }
    } catch (error) {
      console.error('Error removing friend:', error)
      error('  .')
    } finally {
      setRemovingIds(prev => {
        const newSet = new Set(prev)
        newSet.delete(friendId)
        return newSet
      })
    }
  }

  //  
  const filteredTeamMembers = teamMembers.filter(member =>
    member.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    member.email.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const filteredFriends = friends.filter(friend =>
    friend.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    friend.email.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="bg-white rounded-lg shadow">
      {/*  */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-800"> </h2>
          <Button
            onClick={onInviteClick}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
          >
             
          </Button>
        </div>

        {/*  */}
        <div className="flex space-x-1 bg-gray-100 rounded-lg p-1 mb-4">
          <button
            onClick={() => setActiveTab('members')}
            className={`flex-1 py-2 px-4 text-sm font-medium rounded-md transition-colors ${
              activeTab === 'members'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
             ({teamMembers.length})
          </button>
          <button
            onClick={() => setActiveTab('friends')}
            className={`flex-1 py-2 px-4 text-sm font-medium rounded-md transition-colors ${
              activeTab === 'friends'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
             ({friends.length})
          </button>
        </div>

        {/*  */}
        <Input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder={activeTab === 'members' ? ' ...' : ' ...'}
          className="w-full"
        />
      </div>

      {/*  */}
      <div className="p-6">
        {isLoading ? (
          <div className="flex justify-center items-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <div>
            {activeTab === 'members' ? (
              //  
              <div>
                {filteredTeamMembers.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    {searchQuery ? '  .' : ' .   .'}
                  </div>
                ) : (
                  <div className="space-y-4">
                    {filteredTeamMembers.map((member) => (
                      <div key={member.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
                        <div className="flex items-center space-x-4">
                          {/*  */}
                          <div className="w-12 h-12 bg-gray-200 rounded-full flex items-center justify-center overflow-hidden">
                            {member.avatar ? (
                              <img src={member.avatar} alt={member.name} className="w-12 h-12 object-cover" />
                            ) : (
                              <span className="text-lg font-medium text-gray-600">
                                {member.name.charAt(0).toUpperCase()}
                              </span>
                            )}
                          </div>

                          {/*  */}
                          <div>
                            <div className="flex items-center space-x-2">
                              <h3 className="font-medium text-gray-900">{member.name}</h3>
                              <span className={`px-2 py-1 text-xs rounded-full ${
                                member.status === 'active' 
                                  ? 'bg-green-100 text-green-800' 
                                  : 'bg-gray-100 text-gray-600'
                              }`}>
                                {member.status === 'active' ? '' : ''}
                              </span>
                            </div>
                            <div className="text-sm text-gray-500">{member.email}</div>
                            <div className="text-xs text-gray-400 mt-1">
                              {member.role} • : {formatDistanceToNow(new Date(member.joined_at), { addSuffix: true, locale: ko })} • 
                               : {formatDistanceToNow(new Date(member.last_active), { addSuffix: true, locale: ko })}
                            </div>
                          </div>
                        </div>

                        {/*   */}
                        <div className="flex items-center space-x-2">
                          <Button
                            onClick={() => handleRemoveTeamMember(member.id)}
                            disabled={removingIds.has(member.id)}
                            variant="ghost"
                            className="text-red-600 hover:bg-red-50 px-3 py-1 text-sm"
                          >
                            {removingIds.has(member.id) ? ' ...' : ''}
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              //  
              <div>
                {filteredFriends.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    {searchQuery ? '  .' : ' .  .'}
                  </div>
                ) : (
                  <div className="space-y-4">
                    {filteredFriends.map((friend) => (
                      <div key={friend.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
                        <div className="flex items-center space-x-4">
                          {/*  */}
                          <div className="w-12 h-12 bg-gray-200 rounded-full flex items-center justify-center overflow-hidden">
                            {friend.avatar ? (
                              <img src={friend.avatar} alt={friend.name} className="w-12 h-12 object-cover" />
                            ) : (
                              <span className="text-lg font-medium text-gray-600">
                                {friend.name.charAt(0).toUpperCase()}
                              </span>
                            )}
                          </div>

                          {/*  */}
                          <div>
                            <h3 className="font-medium text-gray-900">{friend.name}</h3>
                            <div className="text-sm text-gray-500">{friend.email}</div>
                            <div className="text-xs text-gray-400 mt-1">
                              : {formatDistanceToNow(new Date(friend.added_at), { addSuffix: true, locale: ko })} • 
                               : {friend.projects_shared} • 
                               : {formatDistanceToNow(new Date(friend.last_interaction), { addSuffix: true, locale: ko })}
                            </div>
                          </div>
                        </div>

                        {/*   */}
                        <div className="flex items-center space-x-2">
                          <Button
                            onClick={() => {
                              //    
                              if (onInviteClick) {
                                onInviteClick()
                              }
                            }}
                            className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 text-sm"
                          >
                            
                          </Button>
                          <Button
                            onClick={() => handleRemoveFriend(friend.id)}
                            disabled={removingIds.has(friend.id)}
                            variant="ghost"
                            className="text-red-600 hover:bg-red-50 px-3 py-1 text-sm"
                          >
                            {removingIds.has(friend.id) ? ' ...' : ''}
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default TeamMemberList