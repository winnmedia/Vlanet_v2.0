/**
 * Calendar Service 실시간 동기화 테스트
 * WebSocket 및 Polling 메커니즘 검증
 */

import { describe, test, expect, vi, beforeEach, afterEach } from 'vitest'
import { JSDOM } from 'jsdom'
import { calendarService } from './calendar.service'
import type { CalendarEvent, CalendarUpdateEvent, CalendarSyncListener } from './calendar.service'

// DOM 환경 설정
const dom = new JSDOM('<!DOCTYPE html><html><body></body></html>')
global.document = dom.window.document
global.window = dom.window as any
global.HTMLElement = dom.window.HTMLElement

// WebSocket 모킹
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
    // 비동기적으로 연결 상태로 변경
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
    // 메시지 전송 시뮬레이션
  }
}

// DOM API 모킹
Object.defineProperty(global.window, 'WebSocket', {
  writable: true,
  value: MockWebSocket
})

Object.defineProperty(global.document, 'visibilityState', {
  writable: true,
  value: 'visible'
})

// API Client 모킹
vi.mock('./base', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn()
  }
}))

describe('CalendarService 실시간 동기화', () => {
  let mockApiClient: any
  let mockEvents: CalendarEvent[]
  let mockListener: CalendarSyncListener

  beforeEach(async () => {
    // apiClient 모킹
    const { apiClient } = await import('./base')
    mockApiClient = apiClient

    // 테스트 데이터 준비
    mockEvents = [
      {
        id: 1,
        title: '테스트 일정 1',
        description: '첫 번째 테스트 일정',
        date: '2025-08-09',
        time: '09:00',
        created_at: '2025-08-09T00:00:00Z',
        updated_at: '2025-08-09T00:00:00Z'
      },
      {
        id: 2,
        title: '테스트 일정 2',
        description: '두 번째 테스트 일정',
        date: '2025-08-10',
        time: '14:00',
        created_at: '2025-08-09T00:00:00Z',
        updated_at: '2025-08-09T00:00:00Z'
      }
    ]

    // 기본 API 응답 설정
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

    // 동기화 리스너 모킹
    mockListener = vi.fn()

    // 모든 리스너 제거
    calendarService.stopRealTimeSync()
  })

  afterEach(() => {
    vi.clearAllMocks()
    calendarService.stopRealTimeSync()
  })

  describe('동기화 리스너 관리', () => {
    test('리스너 추가 시 실시간 동기화가 시작된다', () => {
      const startSyncSpy = vi.spyOn(calendarService as any, 'startRealTimeSync')
      
      calendarService.addSyncListener(mockListener)
      expect(startSyncSpy).toHaveBeenCalled()
    })

    test('리스너 제거 시 실시간 동기화가 중지된다', () => {
      const stopSyncSpy = vi.spyOn(calendarService as any, 'stopRealTimeSync')
      
      calendarService.addSyncListener(mockListener)
      calendarService.removeSyncListener(mockListener)
      
      expect(stopSyncSpy).toHaveBeenCalled()
    })

    test('여러 리스너를 관리할 수 있다', () => {
      const listener1 = vi.fn()
      const listener2 = vi.fn()
      
      calendarService.addSyncListener(listener1)
      calendarService.addSyncListener(listener2)
      
      expect((calendarService as any).listeners.size).toBe(2)
      
      calendarService.removeSyncListener(listener1)
      expect((calendarService as any).listeners.size).toBe(1)
    })
  })

  describe('WebSocket 연결 관리', () => {
    test('WebSocket 연결이 성공적으로 초기화된다', async () => {
      calendarService.addSyncListener(mockListener)
      
      // WebSocket 연결 대기
      await new Promise(resolve => setTimeout(resolve, 20))
      
      const wsConnection = (calendarService as any).wsConnection
      expect(wsConnection).toBeInstanceOf(MockWebSocket)
      expect(wsConnection.readyState).toBe(MockWebSocket.OPEN)
    })

    test('WebSocket 메시지를 올바르게 처리한다', async () => {
      calendarService.addSyncListener(mockListener)
      
      // WebSocket 연결 대기
      await new Promise(resolve => setTimeout(resolve, 20))
      
      const wsConnection = (calendarService as any).wsConnection
      const updateEvent: CalendarUpdateEvent = {
        type: 'create',
        event: mockEvents[0],
        timestamp: new Date().toISOString()
      }

      // WebSocket 메시지 시뮬레이션
      wsConnection.onmessage?.({
        data: JSON.stringify(updateEvent)
      } as MessageEvent)

      expect(mockListener).toHaveBeenCalledWith(updateEvent)
    })

    test('WebSocket 연결 오류 시 polling으로 대체된다', async () => {
      const ensurePollingActiveSpy = vi.spyOn(calendarService as any, 'ensurePollingIsActive')
      
      calendarService.addSyncListener(mockListener)
      
      // WebSocket 연결 대기
      await new Promise(resolve => setTimeout(resolve, 20))
      
      const wsConnection = (calendarService as any).wsConnection
      wsConnection.onerror?.(new Event('error'))
      
      expect(ensurePollingActiveSpy).toHaveBeenCalled()
    })

    test('WebSocket 연결 종료 시 재연결을 시도한다', async () => {
      const attemptReconnectionSpy = vi.spyOn(calendarService as any, 'attemptReconnection')
      
      calendarService.addSyncListener(mockListener)
      
      // WebSocket 연결 대기
      await new Promise(resolve => setTimeout(resolve, 20))
      
      const wsConnection = (calendarService as any).wsConnection
      wsConnection.onclose?.(new CloseEvent('close', { code: 1006 })) // 비정상 종료
      
      expect(attemptReconnectionSpy).toHaveBeenCalled()
    })
  })

  describe('Polling 메커니즘', () => {
    beforeEach(() => {
      vi.useFakeTimers()
    })

    afterEach(() => {
      vi.useRealTimers()
    })

    test('실시간 동기화 시작 시 polling이 활성화된다', () => {
      calendarService.addSyncListener(mockListener)
      
      expect((calendarService as any).isPollingActive).toBe(true)
      expect((calendarService as any).pollInterval).toBeTruthy()
    })

    test('주기적으로 업데이트를 확인한다', async () => {
      const checkForUpdatesSpy = vi.spyOn(calendarService as any, 'checkForUpdates')
      
      calendarService.addSyncListener(mockListener)
      
      // 5초 후 polling 실행
      vi.advanceTimersByTime(5000)
      
      expect(checkForUpdatesSpy).toHaveBeenCalled()
    })

    test('업데이트가 있을 때 리스너에게 알린다', async () => {
      const updateData = {
        updates: [
          {
            type: 'update' as const,
            event: { ...mockEvents[0], title: '수정된 제목' },
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
      
      // polling 실행
      await (calendarService as any).checkForUpdates()
      
      expect(mockListener).toHaveBeenCalledWith(updateData.updates[0])
    })
  })

  describe('CRUD 작업 후 동기화', () => {
    test('일정 생성 후 즉시 동기화 확인한다', async () => {
      const checkForUpdatesSpy = vi.spyOn(calendarService as any, 'checkForUpdates')
      
      await calendarService.createEvent({
        title: '새 일정',
        description: '새로운 일정입니다',
        date: '2025-08-11',
        time: '10:00'
      })

      // setTimeout으로 지연된 호출 대기
      await new Promise(resolve => setTimeout(resolve, 150))
      
      expect(checkForUpdatesSpy).toHaveBeenCalled()
    })

    test('일정 수정 후 즉시 동기화 확인한다', async () => {
      const checkForUpdatesSpy = vi.spyOn(calendarService as any, 'checkForUpdates')
      
      await calendarService.updateEvent(1, {
        title: '수정된 일정',
        description: '수정된 설명',
        date: '2025-08-11',
        time: '11:00'
      })

      await new Promise(resolve => setTimeout(resolve, 150))
      
      expect(checkForUpdatesSpy).toHaveBeenCalled()
    })

    test('일정 삭제 후 즉시 동기화 확인한다', async () => {
      const checkForUpdatesSpy = vi.spyOn(calendarService as any, 'checkForUpdates')
      
      await calendarService.deleteEvent(1)

      await new Promise(resolve => setTimeout(resolve, 150))
      
      expect(checkForUpdatesSpy).toHaveBeenCalled()
    })

    test('일괄 업데이트 후 즉시 동기화 확인한다', async () => {
      mockApiClient.post.mockResolvedValueOnce({
        success: true,
        data: mockEvents
      })

      const checkForUpdatesSpy = vi.spyOn(calendarService as any, 'checkForUpdates')
      
      await calendarService.batchUpdateEvents([
        { id: 1, data: { title: '업데이트된 제목 1' } },
        { id: 2, data: { title: '업데이트된 제목 2' } }
      ])

      await new Promise(resolve => setTimeout(resolve, 150))
      
      expect(checkForUpdatesSpy).toHaveBeenCalled()
    })
  })

  describe('페이지 가시성 처리', () => {
    test('페이지가 다시 활성화되면 즉시 업데이트를 확인한다', async () => {
      const checkForUpdatesSpy = vi.spyOn(calendarService as any, 'checkForUpdates')
      
      calendarService.addSyncListener(mockListener)
      
      // 페이지 가시성 변경 시뮬레이션
      Object.defineProperty(document, 'visibilityState', {
        writable: true,
        value: 'visible'
      })

      // visibilitychange 이벤트 발생
      const handleVisibilityChange = (calendarService as any).handleVisibilityChange.bind(calendarService)
      handleVisibilityChange()
      
      expect(checkForUpdatesSpy).toHaveBeenCalled()
    })

    test('WebSocket 연결이 끊어진 경우 재연결을 시도한다', async () => {
      const initializeWebSocketSpy = vi.spyOn(calendarService as any, 'initializeWebSocket')
      
      calendarService.addSyncListener(mockListener)
      
      // WebSocket 연결을 끊어진 상태로 설정
      ;(calendarService as any).wsConnection = null
      
      // 페이지 가시성 변경 시뮬레이션
      const handleVisibilityChange = (calendarService as any).handleVisibilityChange.bind(calendarService)
      handleVisibilityChange()
      
      expect(initializeWebSocketSpy).toHaveBeenCalled()
    })
  })

  describe('오류 처리', () => {
    test('WebSocket 메시지 파싱 오류를 처리한다', async () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      
      calendarService.addSyncListener(mockListener)
      
      // WebSocket 연결 대기
      await new Promise(resolve => setTimeout(resolve, 20))
      
      const wsConnection = (calendarService as any).wsConnection
      
      // 잘못된 JSON 메시지 전송
      wsConnection.onmessage?.({
        data: 'invalid-json'
      } as MessageEvent)

      expect(consoleSpy).toHaveBeenCalledWith('WebSocket 메시지 파싱 오류:', expect.any(Error))
      
      consoleSpy.mockRestore()
    })

    test('리스너 실행 오류를 처리한다', () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      const faultyListener = vi.fn().mockImplementation(() => {
        throw new Error('리스너 오류')
      })
      
      calendarService.addSyncListener(faultyListener)
      
      const updateEvent: CalendarUpdateEvent = {
        type: 'create',
        event: mockEvents[0],
        timestamp: new Date().toISOString()
      }

      ;(calendarService as any).notifyListeners(updateEvent)
      
      expect(consoleSpy).toHaveBeenCalledWith('캘린더 리스너 실행 중 오류:', expect.any(Error))
      
      consoleSpy.mockRestore()
    })

    test('API 업데이트 확인 오류를 처리한다', async () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      
      mockApiClient.get.mockRejectedValueOnce(new Error('네트워크 오류'))
      
      calendarService.addSyncListener(mockListener)
      
      await (calendarService as any).checkForUpdates()
      
      expect(consoleSpy).toHaveBeenCalledWith('캘린더 업데이트 확인 중 오류:', expect.any(Error))
      
      consoleSpy.mockRestore()
    })
  })

  describe('재연결 메커니즘', () => {
    beforeEach(() => {
      vi.useFakeTimers()
    })

    afterEach(() => {
      vi.useRealTimers()
    })

    test('재연결 시도 횟수를 제한한다', () => {
      calendarService.addSyncListener(mockListener)
      
      // 최대 재연결 횟수 설정
      ;(calendarService as any).reconnectAttempts = 5
      ;(calendarService as any).maxReconnectAttempts = 5
      
      const initializeWebSocketSpy = vi.spyOn(calendarService as any, 'initializeWebSocket')
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})
      
      ;(calendarService as any).attemptReconnection()
      
      expect(consoleSpy).toHaveBeenCalledWith('WebSocket 재연결 시도 한계 도달')
      expect(initializeWebSocketSpy).not.toHaveBeenCalled()
      
      consoleSpy.mockRestore()
    })

    test('지수 백오프로 재연결 간격을 증가시킨다', () => {
      calendarService.addSyncListener(mockListener)
      
      ;(calendarService as any).reconnectAttempts = 2
      ;(calendarService as any).reconnectDelay = 1000
      
      const initializeWebSocketSpy = vi.spyOn(calendarService as any, 'initializeWebSocket')
      
      ;(calendarService as any).attemptReconnection()
      
      // 2^2 * 1000 = 4초 후에 재연결 시도
      vi.advanceTimersByTime(4000)
      
      expect(initializeWebSocketSpy).toHaveBeenCalled()
    })
  })

  describe('리소스 정리', () => {
    test('cleanup 호출 시 모든 리소스가 정리된다', () => {
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

    test('페이지 언로드 시 리소스가 정리된다', () => {
      const cleanupSpy = vi.spyOn(calendarService as any, 'cleanup')
      
      calendarService.addSyncListener(mockListener)
      
      // beforeunload 이벤트 시뮬레이션
      const beforeunloadEvent = new Event('beforeunload')
      window.dispatchEvent(beforeunloadEvent)
      
      expect(cleanupSpy).toHaveBeenCalled()
    })
  })
})