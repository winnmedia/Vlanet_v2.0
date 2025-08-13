'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { useToast } from '@/contexts/toast.context'
import { calendarService, type CalendarEvent } from '@/lib/api/calendar.service'
import { invitationService } from '@/lib/api/invitation.service'

export interface NotificationData {
  id: string
  type: 'event_due' | 'event_overdue' | 'invitation_received' | 'invitation_accepted' | 'project_deadline'
  title: string
  message: string
  createdAt: Date
  isRead: boolean
  actionUrl?: string
  priority: 'low' | 'medium' | 'high'
}

interface NotificationContextType {
  notifications: NotificationData[]
  unreadCount: number
  markAsRead: (id: string) => void
  markAllAsRead: () => void
  removeNotification: (id: string) => void
  addNotification: (notification: Omit<NotificationData, 'id' | 'createdAt' | 'isRead'>) => void
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined)

export const useNotifications = () => {
  const context = useContext(NotificationContext)
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider')
  }
  return context
}

interface NotificationProviderProps {
  children: ReactNode
}

export const NotificationProvider = ({ children }: NotificationProviderProps) => {
  const { info, error: showError } = useToast()
  const [notifications, setNotifications] = useState<NotificationData[]>([])

  // 알림 생성 헬퍼 함수
  const generateId = () => `notification-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`

  // 일정 체크 함수
  const checkEventNotifications = async () => {
    try {
      const result = await calendarService.getEvents()
      if (!result.success || !result.data) return

      const now = new Date()
      const events = result.data

      events.forEach((event) => {
        const eventDateTime = new Date(`${event.date}T${event.time}`)
        const diffHours = (eventDateTime.getTime() - now.getTime()) / (1000 * 60 * 60)

        // 24시간 이내 임박 알림
        if (diffHours > 0 && diffHours <= 24) {
          const existingNotification = notifications.find(
            n => n.type === 'event_due' && n.actionUrl === `/calendar?event=${event.id}`
          )

          if (!existingNotification) {
            addNotification({
              type: 'event_due',
              title: '일정 임박',
              message: `"${event.title}"이(가) ${Math.ceil(diffHours)}시간 후 시작됩니다.`,
              priority: diffHours <= 4 ? 'high' : 'medium',
              actionUrl: `/calendar?event=${event.id}`
            })
          }
        }

        // 지연된 일정 알림
        if (diffHours < 0 && Math.abs(diffHours) <= 48) {
          const existingNotification = notifications.find(
            n => n.type === 'event_overdue' && n.actionUrl === `/calendar?event=${event.id}`
          )

          if (!existingNotification) {
            addNotification({
              type: 'event_overdue',
              title: '일정 지연',
              message: `"${event.title}"이(가) ${Math.ceil(Math.abs(diffHours))}시간 지연되었습니다.`,
              priority: 'high',
              actionUrl: `/calendar?event=${event.id}`
            })
          }
        }
      })
    } catch (error) {
      console.error('Error checking event notifications:', error)
    }
  }

  // 초대 알림 체크 함수
  const checkInvitationNotifications = async () => {
    try {
      const result = await invitationService.getReceivedInvitations()
      if (!result.success || !result.data) return

      const pendingInvitations = result.data.filter(inv => inv.status === 'pending')

      pendingInvitations.forEach((invitation) => {
        const existingNotification = notifications.find(
          n => n.type === 'invitation_received' && n.actionUrl === `/invitations?id=${invitation.id}`
        )

        if (!existingNotification) {
          addNotification({
            type: 'invitation_received',
            title: '새 초대',
            message: `${invitation.sender_name || invitation.sender_email}님이 ${invitation.project_title || '프로젝트'}에 초대했습니다.`,
            priority: 'medium',
            actionUrl: `/invitations?id=${invitation.id}`
          })
        }
      })
    } catch (error) {
      console.error('Error checking invitation notifications:', error)
    }
  }

  // 알림 추가
  const addNotification = (notification: Omit<NotificationData, 'id' | 'createdAt' | 'isRead'>) => {
    const newNotification: NotificationData = {
      ...notification,
      id: generateId(),
      createdAt: new Date(),
      isRead: false
    }

    setNotifications(prev => [newNotification, ...prev])

    // 높은 우선순위 알림은 토스트로도 표시
    if (notification.priority === 'high') {
      info(notification.message)
    }
  }

  // 알림 읽음 처리
  const markAsRead = (id: string) => {
    setNotifications(prev =>
      prev.map(notification =>
        notification.id === id ? { ...notification, isRead: true } : notification
      )
    )
  }

  // 모든 알림 읽음 처리
  const markAllAsRead = () => {
    setNotifications(prev =>
      prev.map(notification => ({ ...notification, isRead: true }))
    )
  }

  // 알림 제거
  const removeNotification = (id: string) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id))
  }

  // 읽지 않은 알림 개수
  const unreadCount = notifications.filter(n => !n.isRead).length

  // 주기적 체크 (5분마다)
  useEffect(() => {
    const checkNotifications = () => {
      checkEventNotifications()
      checkInvitationNotifications()
    }

    // 초기 체크
    checkNotifications()

    // 5분마다 체크
    const interval = setInterval(checkNotifications, 5 * 60 * 1000)

    return () => clearInterval(interval)
  }, [])

  // 브라우저 포커스 시 체크
  useEffect(() => {
    const handleFocus = () => {
      checkEventNotifications()
      checkInvitationNotifications()
    }

    window.addEventListener('focus', handleFocus)
    return () => window.removeEventListener('focus', handleFocus)
  }, [])

  // 로컬 스토리지에서 알림 복원
  useEffect(() => {
    const savedNotifications = localStorage.getItem('videoplanet-notifications')
    if (savedNotifications) {
      try {
        const parsed = JSON.parse(savedNotifications)
        setNotifications(parsed.map((n: any) => ({
          ...n,
          createdAt: new Date(n.createdAt)
        })))
      } catch (error) {
        console.error('Error parsing saved notifications:', error)
      }
    }
  }, [])

  // 알림을 로컬 스토리지에 저장
  useEffect(() => {
    localStorage.setItem('videoplanet-notifications', JSON.stringify(notifications))
  }, [notifications])

  const value: NotificationContextType = {
    notifications,
    unreadCount,
    markAsRead,
    markAllAsRead,
    removeNotification,
    addNotification
  }

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  )
}

export default NotificationProvider