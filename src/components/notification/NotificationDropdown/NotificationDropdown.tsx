'use client'

import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/Button'
import { useNotifications } from '../NotificationProvider'
import { formatDistanceToNow } from 'date-fns'
import { ko } from 'date-fns/locale'

const NotificationDropdown = () => {
  const { notifications, unreadCount, markAsRead, markAllAsRead, removeNotification } = useNotifications()
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  // 클릭 외부 영역 감지
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  // 우선순위별 아이콘 및 색상
  const getPriorityInfo = (priority: 'low' | 'medium' | 'high') => {
    switch (priority) {
      case 'high':
        return { icon: '🔴', color: 'text-red-600', bgColor: 'bg-red-50' }
      case 'medium':
        return { icon: '🟡', color: 'text-yellow-600', bgColor: 'bg-yellow-50' }
      case 'low':
        return { icon: '🟢', color: 'text-green-600', bgColor: 'bg-green-50' }
    }
  }

  // 타입별 아이콘
  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'event_due':
        return '⏰'
      case 'event_overdue':
        return '⚠️'
      case 'invitation_received':
        return '📧'
      case 'invitation_accepted':
        return '✅'
      case 'project_deadline':
        return '📅'
      default:
        return '🔔'
    }
  }

  const handleNotificationClick = (notification: typeof notifications[0]) => {
    if (!notification.isRead) {
      markAsRead(notification.id)
    }
    
    if (notification.actionUrl) {
      window.location.href = notification.actionUrl
    }
  }

  return (
    <div className="relative" ref={dropdownRef}>
      {/* 알림 버튼 */}
      <Button
        onClick={() => setIsOpen(!isOpen)}
        variant="ghost"
        className="relative p-2 hover:bg-gray-100 rounded-full"
      >
        <svg 
          className="w-6 h-6 text-gray-600" 
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            strokeWidth={2} 
            d="M15 17h5l-2.405-2.405A2.032 2.032 0 0117 13V11a8.003 8.003 0 00-15.85-2m15.85 2A8.003 8.003 0 00 17 11v2c0 .54-.11 1.08-.405 1.595L15 17z M12 2v1m-8 13h18m-9 4h.01" 
          />
        </svg>
        
        {/* 읽지 않은 알림 개수 뱃지 */}
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </Button>

      {/* 드롭다운 메뉴 */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 bg-white border border-gray-200 rounded-lg shadow-lg z-50 max-h-96 overflow-hidden">
          {/* 헤더 */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-800">
              알림 {unreadCount > 0 && <span className="text-blue-600">({unreadCount})</span>}
            </h3>
            {notifications.length > 0 && (
              <Button
                onClick={markAllAsRead}
                variant="ghost"
                className="text-sm text-blue-600 hover:text-blue-800"
              >
                모두 읽음
              </Button>
            )}
          </div>

          {/* 알림 목록 */}
          <div className="max-h-80 overflow-y-auto">
            {notifications.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                <div className="text-4xl mb-2">🔔</div>
                <p>새로운 알림이 없습니다</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-100">
                {notifications.slice(0, 10).map((notification) => {
                  const priorityInfo = getPriorityInfo(notification.priority)
                  const typeIcon = getTypeIcon(notification.type)

                  return (
                    <div
                      key={notification.id}
                      onClick={() => handleNotificationClick(notification)}
                      className={`p-4 hover:bg-gray-50 cursor-pointer transition-colors ${
                        !notification.isRead ? 'bg-blue-50 border-l-4 border-l-blue-500' : ''
                      }`}
                    >
                      <div className="flex items-start space-x-3">
                        {/* 아이콘 */}
                        <div className={`flex-shrink-0 w-8 h-8 rounded-full ${priorityInfo.bgColor} flex items-center justify-center`}>
                          <span className="text-sm">{typeIcon}</span>
                        </div>

                        {/* 내용 */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between">
                            <h4 className={`text-sm font-medium ${
                              notification.isRead ? 'text-gray-700' : 'text-gray-900'
                            }`}>
                              {notification.title}
                            </h4>
                            <button
                              onClick={(e) => {
                                e.stopPropagation()
                                removeNotification(notification.id)
                              }}
                              className="text-gray-400 hover:text-gray-600 ml-2"
                            >
                              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                              </svg>
                            </button>
                          </div>
                          
                          <p className={`text-sm mt-1 ${
                            notification.isRead ? 'text-gray-500' : 'text-gray-700'
                          }`}>
                            {notification.message}
                          </p>
                          
                          <div className="flex items-center justify-between mt-2">
                            <span className="text-xs text-gray-400">
                              {formatDistanceToNow(notification.createdAt, { 
                                addSuffix: true, 
                                locale: ko 
                              })}
                            </span>
                            <span className={`text-xs px-2 py-1 rounded-full ${priorityInfo.bgColor} ${priorityInfo.color}`}>
                              {notification.priority === 'high' ? '긴급' : 
                               notification.priority === 'medium' ? '보통' : '낮음'}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </div>

          {/* 더 보기 링크 */}
          {notifications.length > 10 && (
            <div className="p-3 border-t border-gray-200 text-center">
              <Button
                onClick={() => {
                  setIsOpen(false)
                  window.location.href = '/notifications'
                }}
                variant="ghost"
                className="text-sm text-blue-600 hover:text-blue-800"
              >
                모든 알림 보기 ({notifications.length - 10}개 더)
              </Button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default NotificationDropdown