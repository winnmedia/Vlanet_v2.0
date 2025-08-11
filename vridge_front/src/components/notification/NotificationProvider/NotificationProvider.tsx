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

  //    
  const generateId = () => `notification-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`

  //   
  const checkEventNotifications = async () => {
    try {
      const result = await calendarService.getEvents()
      if (!result.success || !result.data) return

      const now = new Date()
      const events = result.data

      events.forEach((event) => {
        const eventDateTime = new Date(`${event.date}T${event.time}`)
        const diffHours = (eventDateTime.getTime() - now.getTime()) / (1000 * 60 * 60)

        // 24   
        if (diffHours > 0 && diffHours <= 24) {
          const existingNotification = notifications.find(
            n => n.type === 'event_due' && n.actionUrl === `/calendar?event=${event.id}`
          )

          if (!existingNotification) {
            addNotification({
              type: 'event_due',
              title: ' ',
              message: `"${event.title}"() ${Math.ceil(diffHours)}  .`,
              priority: diffHours <= 4 ? 'high' : 'medium',
              actionUrl: `/calendar?event=${event.id}`
            })
          }
        }

        //   
        if (diffHours < 0 && Math.abs(diffHours) <= 48) {
          const existingNotification = notifications.find(
            n => n.type === 'event_overdue' && n.actionUrl === `/calendar?event=${event.id}`
          )

          if (!existingNotification) {
            addNotification({
              type: 'event_overdue',
              title: ' ',
              message: `"${event.title}"() ${Math.ceil(Math.abs(diffHours))} .`,
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

  //    
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
            title: ' ',
            message: `${invitation.sender_name || invitation.sender_email} ${invitation.project_title || ''} .`,
            priority: 'medium',
            actionUrl: `/invitations?id=${invitation.id}`
          })
        }
      })
    } catch (error) {
      console.error('Error checking invitation notifications:', error)
    }
  }

  //  
  const addNotification = (notification: Omit<NotificationData, 'id' | 'createdAt' | 'isRead'>) => {
    const newNotification: NotificationData = {
      ...notification,
      id: generateId(),
      createdAt: new Date(),
      isRead: false
    }

    setNotifications(prev => [newNotification, ...prev])

    //     
    if (notification.priority === 'high') {
      info(notification.message)
    }
  }

  //   
  const markAsRead = (id: string) => {
    setNotifications(prev =>
      prev.map(notification =>
        notification.id === id ? { ...notification, isRead: true } : notification
      )
    )
  }

  //    
  const markAllAsRead = () => {
    setNotifications(prev =>
      prev.map(notification => ({ ...notification, isRead: true }))
    )
  }

  //  
  const removeNotification = (id: string) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id))
  }

  //    
  const unreadCount = notifications.filter(n => !n.isRead).length

  //   (5)
  useEffect(() => {
    const checkNotifications = () => {
      checkEventNotifications()
      checkInvitationNotifications()
    }

    //  
    checkNotifications()

    // 5 
    const interval = setInterval(checkNotifications, 5 * 60 * 1000)

    return () => clearInterval(interval)
  }, [])

  //    
  useEffect(() => {
    const handleFocus = () => {
      checkEventNotifications()
      checkInvitationNotifications()
    }

    window.addEventListener('focus', handleFocus)
    return () => window.removeEventListener('focus', handleFocus)
  }, [])

  //    
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

  //    
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