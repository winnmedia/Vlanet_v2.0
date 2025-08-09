'use client'

import { useState, useEffect } from 'react'
import DashboardLayout from '@/components/layout/DashboardLayout'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Modal } from '@/components/ui/Modal'
import { useToast } from '@/contexts/toast.context'
import { calendarService, type CalendarEvent, type CreateCalendarEventData } from '@/lib/api/calendar.service'
import { Calendar } from '@/components/calendar/Calendar'
import { InviteModal } from '@/components/invitation/InviteModal'
import { InvitationList } from '@/components/invitation/InvitationList'
import { TeamMemberList } from '@/components/team/TeamMemberList'
import { NotificationProvider } from '@/components/notification/NotificationProvider'
import { NotificationDropdown } from '@/components/notification/NotificationDropdown'
import type { DateSelectArg, EventClickArg, EventDropArg } from '@fullcalendar/core'

interface EventFormData extends CreateCalendarEventData {}

const CalendarPageContent = () => {
  const { success, error } = useToast()
  const [events, setEvents] = useState<CalendarEvent[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [showEventModal, setShowEventModal] = useState(false)
  const [showInviteModal, setShowInviteModal] = useState(false)
  const [editingEvent, setEditingEvent] = useState<CalendarEvent | null>(null)
  const [activeTab, setActiveTab] = useState<'calendar' | 'invitations' | 'team'>('calendar')
  const [formData, setFormData] = useState<EventFormData>({
    title: '',
    description: '',
    date: '',
    time: ''
  })

  // API 서비스 함수들
  const fetchEvents = async () => {
    try {
      const result = await calendarService.getEvents()
      if (result.success && result.data) {
        setEvents(result.data)
      } else {
        throw new Error(result.error?.message || 'Failed to fetch events')
      }
    } catch (error) {
      console.error('Error fetching events:', error)
      error('일정을 불러오는데 실패했습니다.')
    } finally {
      setIsLoading(false)
    }
  }

  const createEvent = async (eventData: EventFormData) => {
    try {
      const result = await calendarService.createEvent(eventData)
      if (result.success && result.data) {
        setEvents(prev => [...prev, result.data])
        success('일정이 생성되었습니다.')
      } else {
        throw new Error(result.error?.message || 'Failed to create event')
      }
    } catch (error) {
      console.error('Error creating event:', error)
      error('일정 생성에 실패했습니다.')
    }
  }

  const updateEvent = async (id: number, eventData: EventFormData) => {
    try {
      const result = await calendarService.updateEvent(id, eventData)
      if (result.success && result.data) {
        setEvents(prev => prev.map(event => 
          event.id === id ? result.data : event
        ))
        success('일정이 수정되었습니다.')
      } else {
        throw new Error(result.error?.message || 'Failed to update event')
      }
    } catch (error) {
      console.error('Error updating event:', error)
      error('일정 수정에 실패했습니다.')
    }
  }

  const deleteEvent = async (id: number) => {
    try {
      const result = await calendarService.deleteEvent(id)
      if (result.success) {
        setEvents(prev => prev.filter(event => event.id !== id))
        success('일정이 삭제되었습니다.')
      } else {
        throw new Error(result.error?.message || 'Failed to delete event')
      }
    } catch (error) {
      console.error('Error deleting event:', error)
      error('일정 삭제에 실패했습니다.')
    }
  }

  useEffect(() => {
    fetchEvents()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (editingEvent) {
      await updateEvent(editingEvent.id, formData)
    } else {
      await createEvent(formData)
    }
    
    setShowEventModal(false)
    setEditingEvent(null)
    setFormData({ title: '', description: '', date: '', time: '' })
  }

  // 캘린더에서 날짜 선택 시 새 이벤트 생성
  const handleDateSelect = (selectInfo: DateSelectArg) => {
    const selectedDate = selectInfo.startStr.split('T')[0]
    const selectedTime = new Date().toTimeString().substring(0, 5)
    
    setFormData({
      title: '',
      description: '',
      date: selectedDate,
      time: selectedTime
    })
    setEditingEvent(null)
    setShowEventModal(true)
  }

  // 캘린더에서 이벤트 클릭 시 수정
  const handleEventClick = (clickInfo: EventClickArg) => {
    const originalEvent = clickInfo.event.extendedProps.originalEvent as CalendarEvent
    setEditingEvent(originalEvent)
    setFormData({
      title: originalEvent.title,
      description: originalEvent.description,
      date: originalEvent.date,
      time: originalEvent.time
    })
    setShowEventModal(true)
  }

  // 캘린더에서 이벤트 드래그 시 업데이트
  const handleEventDrop = async (dropInfo: EventDropArg) => {
    const eventId = parseInt(dropInfo.event.id)
    const newDate = dropInfo.event.startStr.split('T')[0]
    const newTime = dropInfo.event.startStr.split('T')[1]?.substring(0, 5) || '00:00'
    
    const originalEvent = events.find(e => e.id === eventId)
    if (originalEvent) {
      await updateEvent(eventId, {
        ...originalEvent,
        date: newDate,
        time: newTime
      })
    }
  }

  const handleDelete = (id: number) => {
    if (window.confirm('정말로 이 일정을 삭제하시겠습니까?')) {
      deleteEvent(id)
    }
  }

  const resetForm = () => {
    setFormData({ title: '', description: '', date: '', time: '' })
    setEditingEvent(null)
    setShowEventModal(false)
  }

  // 오늘 날짜 기본값 설정
  const today = new Date().toISOString().split('T')[0]

  return (
    <DashboardLayout>
      <div className="p-6">
        {/* 헤더 */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">프로젝트 관리</h1>
            <p className="text-gray-600 mt-1">일정, 초대, 팀원을 한 곳에서 관리하세요</p>
          </div>
          <div className="flex items-center space-x-4">
            <NotificationDropdown />
            <div className="flex space-x-2">
              <Button 
                onClick={() => setShowEventModal(true)}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
              >
                새 일정 추가
              </Button>
              <Button 
                onClick={() => setShowInviteModal(true)}
                className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg"
              >
                팀원 초대
              </Button>
            </div>
          </div>
        </div>

        {/* 탭 네비게이션 */}
        <div className="flex space-x-1 bg-gray-100 rounded-lg p-1 mb-6">
          <button
            onClick={() => setActiveTab('calendar')}
            className={`flex-1 py-3 px-4 text-sm font-medium rounded-md transition-colors ${
              activeTab === 'calendar'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            📅 캘린더
          </button>
          <button
            onClick={() => setActiveTab('invitations')}
            className={`flex-1 py-3 px-4 text-sm font-medium rounded-md transition-colors ${
              activeTab === 'invitations'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            📧 초대 관리
          </button>
          <button
            onClick={() => setActiveTab('team')}
            className={`flex-1 py-3 px-4 text-sm font-medium rounded-md transition-colors ${
              activeTab === 'team'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            👥 팀 관리
          </button>
        </div>

        {/* 탭 컨텐츠 */}
        <div>
          {activeTab === 'calendar' && (
            <Calendar
              events={events}
              onEventCreate={handleDateSelect}
              onEventEdit={handleEventClick}
              onEventDelete={handleDelete}
              onEventUpdate={handleEventDrop}
              isLoading={isLoading}
            />
          )}

          {activeTab === 'invitations' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white rounded-lg shadow">
                  <div className="p-4 border-b border-gray-200">
                    <h3 className="text-lg font-semibold text-gray-800">받은 초대</h3>
                  </div>
                  <div className="p-4">
                    <InvitationList 
                      type="received" 
                      onInvitationUpdate={() => {
                        // 필요시 상태 업데이트
                      }}
                    />
                  </div>
                </div>

                <div className="bg-white rounded-lg shadow">
                  <div className="p-4 border-b border-gray-200">
                    <h3 className="text-lg font-semibold text-gray-800">보낸 초대</h3>
                  </div>
                  <div className="p-4">
                    <InvitationList 
                      type="sent" 
                      onInvitationUpdate={() => {
                        // 필요시 상태 업데이트
                      }}
                    />
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'team' && (
            <TeamMemberList
              onInviteClick={() => setShowInviteModal(true)}
            />
          )}
        </div>

        {/* 일정 추가/수정 모달 */}
        <Modal
          isOpen={showEventModal}
          onClose={resetForm}
          title={editingEvent ? '일정 수정' : '새 일정 추가'}
        >
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                제목
              </label>
              <Input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                required
                className="w-full"
                placeholder="일정 제목을 입력하세요"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                설명
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                rows={3}
                placeholder="일정 설명을 입력하세요"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                날짜
              </label>
              <Input
                type="date"
                value={formData.date}
                onChange={(e) => setFormData(prev => ({ ...prev, date: e.target.value }))}
                required
                min={today}
                className="w-full"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                시간
              </label>
              <Input
                type="time"
                value={formData.time}
                onChange={(e) => setFormData(prev => ({ ...prev, time: e.target.value }))}
                required
                className="w-full"
              />
            </div>
            
            <div className="flex space-x-3 pt-4">
              <Button
                type="submit"
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg"
              >
                {editingEvent ? '수정하기' : '추가하기'}
              </Button>
              <Button
                type="button"
                onClick={resetForm}
                variant="ghost"
                className="flex-1 border border-gray-300 hover:bg-gray-50 py-2 rounded-lg"
              >
                취소
              </Button>
            </div>
          </form>
        </Modal>

        {/* 팀원 초대 모달 */}
        <InviteModal
          isOpen={showInviteModal}
          onClose={() => setShowInviteModal(false)}
          onInviteSent={() => {
            // 초대 발송 후 필요한 상태 업데이트
          }}
        />
      </div>
    </DashboardLayout>
  )
}

const CalendarPage = () => {
  return (
    <NotificationProvider>
      <CalendarPageContent />
    </NotificationProvider>
  )
}

export default CalendarPage