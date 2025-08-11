/**
 * Calendar Service   
 * WebSocket  Polling  
 */

import { describe, test, expect, vi, beforeEach, afterEach } from 'vitest'
import { JSDOM } from 'jsdom'
import { calendarService } from './calendar.service'
import type { CalendarEvent, CalendarUpdateEvent, CalendarSyncListener } from './calendar.service'

// DOM  
const dom = new JSDOM('<!DOCTYPE html><html><body></body></html>')
global.document = dom.window.document
global.window = dom.window as any
global.HTMLElement = dom.window.HTMLElement

// WebSocket 
class MockWebSocket {
  static CONNECTING = 0
  static OPEN = 1
  static CLOSING = 2
  static CLOSED = 3

  readyState = MockWebSocket.CONNECTING
  onopen: ((event: Event) => void) | null = null
  onclose: ((event: CloseEvent) => void) | null = null
  onmessage: ((event: MessageEvent) => void) | null = null
  onerror: ((event: Event) => void) | null = null

  constructor(public url: string) {
    //    
    setTimeout(() => {
      this.readyState = MockWebSocket.OPEN
      this.onopen?.(new Event('open'))
    }, 10)
  }

  close(code?: number, reason?: string) {
    this.readyState = MockWebSocket.CLOSED
    this.onclose?.(new CloseEvent('close', { code, reason }))
  }

  send(data: string) {
    //   
  }
}

// DOM API 
Object.defineProperty(global.window, 'WebSocket', {
  writable: true,
  value: MockWebSocket
})

Object.defineProperty(global.document, 'visibilityState', {
  writable: true,
  value: 'visible'
})

// API Client 
vi.mock('./base', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn()
  }
}))

describe('CalendarService  ', () => {
  let mockApiClient: any
  let mockEvents: CalendarEvent[]
  let mockListener: CalendarSyncListener

  beforeEach(async () => {
    // apiClient 
    const { apiClient } = await import('./base')
    mockApiClient = apiClient

    //   
    mockEvents = [
      {
        id: 1,
        title: '  1',
        description: '   ',
        date: '2025-08-09',
        time: '09:00',
        created_at: '2025-08-09T00:00:00Z',
        updated_at: '2025-08-09T00:00:00Z'
      },
      {
        id: 2,
        title: '  2',
        description: '   ',
        date: '2025-08-10',
        time: '14:00',
        created_at: '2025-08-09T00:00:00Z',
        updated_at: '2025-08-09T00:00:00Z'
      }
    ]

    //  API  
    mockApiClient.get.mockResolvedValue({
      success: true,
      data: mockEvents
    })

    mockApiClient.post.mockResolvedValue({
      success: true,
      data: mockEvents[0]
    })

    mockApiClient.put.mockResolvedValue({
      success: true,
      data: mockEvents[0]
    })

    mockApiClient.patch.mockResolvedValue({
      success: true,
      data: mockEvents[0]
    })

    mockApiClient.delete.mockResolvedValue({
      success: true,
      data: null
    })

    //   
    mockListener = vi.fn()

    //   
    calendarService.stopRealTimeSync()
  })

  afterEach(() => {
    vi.clearAllMocks()
    calendarService.stopRealTimeSync()
  })

  describe('  ', () => {
    test('     ', () => {
      const startSyncSpy = vi.spyOn(calendarService as any, 'startRealTimeSync')
      
      calendarService.addSyncListener(mockListener)
      expect(startSyncSpy).toHaveBeenCalled()
    })

    test('     ', () => {
      const stopSyncSpy = vi.spyOn(calendarService as any, 'stopRealTimeSync')
      
      calendarService.addSyncListener(mockListener)
      calendarService.removeSyncListener(mockListener)
      
      expect(stopSyncSpy).toHaveBeenCalled()
    })

    test('    ', () => {
      const listener1 = vi.fn()
      const listener2 = vi.fn()
      
      calendarService.addSyncListener(listener1)
      calendarService.addSyncListener(listener2)
      
      expect((calendarService as any).listeners.size).toBe(2)
      
      calendarService.removeSyncListener(listener1)
      expect((calendarService as any).listeners.size).toBe(1)
    })
  })

  describe('WebSocket  ', () => {
    test('WebSocket   ', async () => {
      calendarService.addSyncListener(mockListener)
      
      // WebSocket  
      await new Promise(resolve => setTimeout(resolve, 20))
      
      const wsConnection = (calendarService as any).wsConnection
      expect(wsConnection).toBeInstanceOf(MockWebSocket)
      expect(wsConnection.readyState).toBe(MockWebSocket.OPEN)
    })

    test('WebSocket   ', async () => {
      calendarService.addSyncListener(mockListener)
      
      // WebSocket  
      await new Promise(resolve => setTimeout(resolve, 20))
      
      const wsConnection = (calendarService as any).wsConnection
      const updateEvent: CalendarUpdateEvent = {
        type: 'create',
        event: mockEvents[0],
        timestamp: new Date().toISOString()
      }

      // WebSocket  
      wsConnection.onmessage?.({
        data: JSON.stringify(updateEvent)
      } as MessageEvent)

      expect(mockListener).toHaveBeenCalledWith(updateEvent)
    })

    test('WebSocket    polling ', async () => {
      const ensurePollingActiveSpy = vi.spyOn(calendarService as any, 'ensurePollingIsActive')
      
      calendarService.addSyncListener(mockListener)
      
      // WebSocket  
      await new Promise(resolve => setTimeout(resolve, 20))
      
      const wsConnection = (calendarService as any).wsConnection
      wsConnection.onerror?.(new Event('error'))
      
      expect(ensurePollingActiveSpy).toHaveBeenCalled()
    })

    test('WebSocket     ', async () => {
      const attemptReconnectionSpy = vi.spyOn(calendarService as any, 'attemptReconnection')
      
      calendarService.addSyncListener(mockListener)
      
      // WebSocket  
      await new Promise(resolve => setTimeout(resolve, 20))
      
      const wsConnection = (calendarService as any).wsConnection
      wsConnection.onclose?.(new CloseEvent('close', { code: 1006 })) //  
      
      expect(attemptReconnectionSpy).toHaveBeenCalled()
    })
  })

  describe('Polling ', () => {
    beforeEach(() => {
      vi.useFakeTimers()
    })

    afterEach(() => {
      vi.useRealTimers()
    })

    test('    polling ', () => {
      calendarService.addSyncListener(mockListener)
      
      expect((calendarService as any).isPollingActive).toBe(true)
      expect((calendarService as any).pollInterval).toBeTruthy()
    })

    test('  ', async () => {
      const checkForUpdatesSpy = vi.spyOn(calendarService as any, 'checkForUpdates')
      
      calendarService.addSyncListener(mockListener)
      
      // 5  polling 
      vi.advanceTimersByTime(5000)
      
      expect(checkForUpdatesSpy).toHaveBeenCalled()
    })

    test('    ', async () => {
      const updateData = {
        updates: [
          {
            type: 'update' as const,
            event: { ...mockEvents[0], title: ' ' },
            timestamp: new Date().toISOString()
          }
        ],
        latest_timestamp: new Date().toISOString()
      }

      mockApiClient.get.mockResolvedValueOnce({
        success: true,
        data: updateData
      })

      calendarService.addSyncListener(mockListener)
      
      // polling 
      await (calendarService as any).checkForUpdates()
      
      expect(mockListener).toHaveBeenCalledWith(updateData.updates[0])
    })
  })

  describe('CRUD   ', () => {
    test('     ', async () => {
      const checkForUpdatesSpy = vi.spyOn(calendarService as any, 'checkForUpdates')
      
      await calendarService.createEvent({
        title: ' ',
        description: ' ',
        date: '2025-08-11',
        time: '10:00'
      })

      // setTimeout   
      await new Promise(resolve => setTimeout(resolve, 150))
      
      expect(checkForUpdatesSpy).toHaveBeenCalled()
    })

    test('     ', async () => {
      const checkForUpdatesSpy = vi.spyOn(calendarService as any, 'checkForUpdates')
      
      await calendarService.updateEvent(1, {
        title: ' ',
        description: ' ',
        date: '2025-08-11',
        time: '11:00'
      })

      await new Promise(resolve => setTimeout(resolve, 150))
      
      expect(checkForUpdatesSpy).toHaveBeenCalled()
    })

    test('     ', async () => {
      const checkForUpdatesSpy = vi.spyOn(calendarService as any, 'checkForUpdates')
      
      await calendarService.deleteEvent(1)

      await new Promise(resolve => setTimeout(resolve, 150))
      
      expect(checkForUpdatesSpy).toHaveBeenCalled()
    })

    test('     ', async () => {
      mockApiClient.post.mockResolvedValueOnce({
        success: true,
        data: mockEvents
      })

      const checkForUpdatesSpy = vi.spyOn(calendarService as any, 'checkForUpdates')
      
      await calendarService.batchUpdateEvents([
        { id: 1, data: { title: '  1' } },
        { id: 2, data: { title: '  2' } }
      ])

      await new Promise(resolve => setTimeout(resolve, 150))
      
      expect(checkForUpdatesSpy).toHaveBeenCalled()
    })
  })

  describe('  ', () => {
    test('     ', async () => {
      const checkForUpdatesSpy = vi.spyOn(calendarService as any, 'checkForUpdates')
      
      calendarService.addSyncListener(mockListener)
      
      //    
      Object.defineProperty(document, 'visibilityState', {
        writable: true,
        value: 'visible'
      })

      // visibilitychange  
      const handleVisibilityChange = (calendarService as any).handleVisibilityChange.bind(calendarService)
      handleVisibilityChange()
      
      expect(checkForUpdatesSpy).toHaveBeenCalled()
    })

    test('WebSocket     ', async () => {
      const initializeWebSocketSpy = vi.spyOn(calendarService as any, 'initializeWebSocket')
      
      calendarService.addSyncListener(mockListener)
      
      // WebSocket    
      ;(calendarService as any).wsConnection = null
      
      //    
      const handleVisibilityChange = (calendarService as any).handleVisibilityChange.bind(calendarService)
      handleVisibilityChange()
      
      expect(initializeWebSocketSpy).toHaveBeenCalled()
    })
  })

  describe(' ', () => {
    test('WebSocket    ', async () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      
      calendarService.addSyncListener(mockListener)
      
      // WebSocket  
      await new Promise(resolve => setTimeout(resolve, 20))
      
      const wsConnection = (calendarService as any).wsConnection
      
      //  JSON  
      wsConnection.onmessage?.({
        data: 'invalid-json'
      } as MessageEvent)

      expect(consoleSpy).toHaveBeenCalledWith('WebSocket   :', expect.any(Error))
      
      consoleSpy.mockRestore()
    })

    test('   ', () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      const faultyListener = vi.fn().mockImplementation(() => {
        throw new Error(' ')
      })
      
      calendarService.addSyncListener(faultyListener)
      
      const updateEvent: CalendarUpdateEvent = {
        type: 'create',
        event: mockEvents[0],
        timestamp: new Date().toISOString()
      }

      ;(calendarService as any).notifyListeners(updateEvent)
      
      expect(consoleSpy).toHaveBeenCalledWith('    :', expect.any(Error))
      
      consoleSpy.mockRestore()
    })

    test('API    ', async () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      
      mockApiClient.get.mockRejectedValueOnce(new Error(' '))
      
      calendarService.addSyncListener(mockListener)
      
      await (calendarService as any).checkForUpdates()
      
      expect(consoleSpy).toHaveBeenCalledWith('    :', expect.any(Error))
      
      consoleSpy.mockRestore()
    })
  })

  describe(' ', () => {
    beforeEach(() => {
      vi.useFakeTimers()
    })

    afterEach(() => {
      vi.useRealTimers()
    })

    test('   ', () => {
      calendarService.addSyncListener(mockListener)
      
      //    
      ;(calendarService as any).reconnectAttempts = 5
      ;(calendarService as any).maxReconnectAttempts = 5
      
      const initializeWebSocketSpy = vi.spyOn(calendarService as any, 'initializeWebSocket')
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})
      
      ;(calendarService as any).attemptReconnection()
      
      expect(consoleSpy).toHaveBeenCalledWith('WebSocket    ')
      expect(initializeWebSocketSpy).not.toHaveBeenCalled()
      
      consoleSpy.mockRestore()
    })

    test('    ', () => {
      calendarService.addSyncListener(mockListener)
      
      ;(calendarService as any).reconnectAttempts = 2
      ;(calendarService as any).reconnectDelay = 1000
      
      const initializeWebSocketSpy = vi.spyOn(calendarService as any, 'initializeWebSocket')
      
      ;(calendarService as any).attemptReconnection()
      
      // 2^2 * 1000 = 4   
      vi.advanceTimersByTime(4000)
      
      expect(initializeWebSocketSpy).toHaveBeenCalled()
    })
  })

  describe(' ', () => {
    test('cleanup     ', () => {
      calendarService.addSyncListener(mockListener)
      
      const pollInterval = (calendarService as any).pollInterval
      const wsConnection = (calendarService as any).wsConnection
      
      expect(pollInterval).toBeTruthy()
      expect((calendarService as any).listeners.size).toBe(1)
      
      ;(calendarService as any).cleanup()
      
      expect((calendarService as any).isPollingActive).toBe(false)
      expect((calendarService as any).pollInterval).toBeNull()
      expect((calendarService as any).listeners.size).toBe(0)
    })

    test('    ', () => {
      const cleanupSpy = vi.spyOn(calendarService as any, 'cleanup')
      
      calendarService.addSyncListener(mockListener)
      
      // beforeunload  
      const beforeunloadEvent = new Event('beforeunload')
      window.dispatchEvent(beforeunloadEvent)
      
      expect(cleanupSpy).toHaveBeenCalled()
    })
  })
})