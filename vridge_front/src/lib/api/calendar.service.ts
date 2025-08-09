import { apiClient } from './base';
import type { APIResponse } from '@/types';

export interface CalendarEvent {
  id: number;
  title: string;
  description: string;
  date: string;
  time: string;
  created_at: string;
  updated_at: string;
}

export interface CreateCalendarEventData {
  title: string;
  description: string;
  date: string;
  time: string;
}

export interface UpdateCalendarEventData extends Partial<CreateCalendarEventData> {}

// 실시간 업데이트 이벤트 타입
export interface CalendarUpdateEvent {
  type: 'create' | 'update' | 'delete' | 'bulk_update';
  event?: CalendarEvent;
  eventId?: number;
  events?: CalendarEvent[];
  timestamp: string;
}

// 캘린더 동기화 리스너 타입
export type CalendarSyncListener = (update: CalendarUpdateEvent) => void;

/**
 * Calendar API 서비스 클래스
 * 실시간 동기화 및 일정 관리 CRUD 기능을 제공합니다.
 */
class CalendarService {
  private readonly endpoint = '/api/calendar';
  private listeners: Set<CalendarSyncListener> = new Set();
  private wsConnection: WebSocket | null = null;
  private pollInterval: NodeJS.Timeout | null = null;
  private lastSyncTimestamp: string | null = null;
  private isPollingActive: boolean = false;
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 5;
  private reconnectDelay: number = 1000; // 1초에서 시작

  constructor() {
    // 페이지 언로드 시 연결 정리
    if (typeof window !== 'undefined') {
      window.addEventListener('beforeunload', this.cleanup.bind(this));
      window.addEventListener('visibilitychange', this.handleVisibilityChange.bind(this));
    }
  }

  /**
   * 실시간 동기화 시작
   */
  startRealTimeSync(): void {
    this.initializeWebSocket();
    this.startPolling();
  }

  /**
   * 실시간 동기화 중지
   */
  stopRealTimeSync(): void {
    this.cleanup();
  }

  /**
   * 동기화 이벤트 리스너 추가
   */
  addSyncListener(listener: CalendarSyncListener): void {
    this.listeners.add(listener);
    
    // 첫 번째 리스너 추가 시 자동으로 동기화 시작
    if (this.listeners.size === 1) {
      this.startRealTimeSync();
    }
  }

  /**
   * 동기화 이벤트 리스너 제거
   */
  removeSyncListener(listener: CalendarSyncListener): void {
    this.listeners.delete(listener);
    
    // 마지막 리스너 제거 시 동기화 중지
    if (this.listeners.size === 0) {
      this.stopRealTimeSync();
    }
  }

  /**
   * WebSocket 연결 초기화
   */
  private initializeWebSocket(): void {
    if (typeof window === 'undefined') return;

    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/ws/calendar/`;
      
      this.wsConnection = new WebSocket(wsUrl);

      this.wsConnection.onopen = this.handleWebSocketOpen.bind(this);
      this.wsConnection.onmessage = this.handleWebSocketMessage.bind(this);
      this.wsConnection.onclose = this.handleWebSocketClose.bind(this);
      this.wsConnection.onerror = this.handleWebSocketError.bind(this);

    } catch (error) {
      console.warn('WebSocket 연결 초기화 실패:', error);
      // WebSocket 실패 시 polling으로 대체
      this.ensurePollingIsActive();
    }
  }

  /**
   * WebSocket 연결 성공 처리
   */
  private handleWebSocketOpen(): void {
    console.log('캘린더 WebSocket 연결 성공');
    this.reconnectAttempts = 0;
    this.reconnectDelay = 1000;
    
    // WebSocket 연결 성공 시 polling 빈도 줄이기
    if (this.isPollingActive) {
      this.restartPolling(30000); // 30초로 연장
    }
  }

  /**
   * WebSocket 메시지 처리
   */
  private handleWebSocketMessage(event: MessageEvent): void {
    try {
      const data = JSON.parse(event.data) as CalendarUpdateEvent;
      this.lastSyncTimestamp = data.timestamp;
      this.notifyListeners(data);
    } catch (error) {
      console.error('WebSocket 메시지 파싱 오류:', error);
    }
  }

  /**
   * WebSocket 연결 종료 처리
   */
  private handleWebSocketClose(event: CloseEvent): void {
    console.log('캘린더 WebSocket 연결 종료:', event.code);
    this.wsConnection = null;

    // 의도적 종료가 아닌 경우 재연결 시도
    if (event.code !== 1000 && this.listeners.size > 0) {
      this.attemptReconnection();
    }

    // WebSocket 연결 종료 시 polling 활성화
    this.ensurePollingIsActive();
  }

  /**
   * WebSocket 오류 처리
   */
  private handleWebSocketError(error: Event): void {
    console.error('캘린더 WebSocket 오류:', error);
    this.ensurePollingIsActive();
  }

  /**
   * WebSocket 재연결 시도
   */
  private attemptReconnection(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.warn('WebSocket 재연결 시도 한계 도달');
      return;
    }

    this.reconnectAttempts++;
    const delay = Math.min(this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1), 30000);

    setTimeout(() => {
      if (this.listeners.size > 0) {
        console.log(`WebSocket 재연결 시도 ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
        this.initializeWebSocket();
      }
    }, delay);
  }

  /**
   * Polling 시작
   */
  private startPolling(): void {
    this.isPollingActive = true;
    this.restartPolling(5000); // 기본 5초 간격
  }

  /**
   * Polling 재시작
   */
  private restartPolling(interval: number): void {
    if (this.pollInterval) {
      clearInterval(this.pollInterval);
    }

    this.pollInterval = setInterval(async () => {
      await this.checkForUpdates();
    }, interval);
  }

  /**
   * Polling이 활성화되어 있는지 확인하고 필요시 시작
   */
  private ensurePollingIsActive(): void {
    if (!this.isPollingActive && this.listeners.size > 0) {
      this.startPolling();
    }
  }

  /**
   * 서버에서 업데이트 확인 (Polling)
   */
  private async checkForUpdates(): Promise<void> {
    try {
      const url = this.lastSyncTimestamp 
        ? `${this.endpoint}/updates/?since=${encodeURIComponent(this.lastSyncTimestamp)}`
        : `${this.endpoint}/updates/`;

      const response = await apiClient.get<{
        updates: CalendarUpdateEvent[];
        latest_timestamp: string;
      }>(url);

      if (response.success && response.data && response.data.updates.length > 0) {
        this.lastSyncTimestamp = response.data.latest_timestamp;
        
        // 각 업데이트를 리스너에게 알림
        response.data.updates.forEach(update => {
          this.notifyListeners(update);
        });
      }
    } catch (error) {
      console.error('캘린더 업데이트 확인 중 오류:', error);
    }
  }

  /**
   * 리스너들에게 업데이트 알림
   */
  private notifyListeners(update: CalendarUpdateEvent): void {
    this.listeners.forEach(listener => {
      try {
        listener(update);
      } catch (error) {
        console.error('캘린더 리스너 실행 중 오류:', error);
      }
    });
  }

  /**
   * 페이지 가시성 변경 처리
   */
  private handleVisibilityChange(): void {
    if (document.visibilityState === 'visible') {
      // 페이지가 다시 활성화되면 즉시 업데이트 확인
      this.checkForUpdates();
      
      // WebSocket 연결이 끊어져 있으면 재연결 시도
      if (!this.wsConnection || this.wsConnection.readyState !== WebSocket.OPEN) {
        this.initializeWebSocket();
      }
    }
  }

  /**
   * 연결 및 리소스 정리
   */
  private cleanup(): void {
    this.isPollingActive = false;

    if (this.pollInterval) {
      clearInterval(this.pollInterval);
      this.pollInterval = null;
    }

    if (this.wsConnection) {
      this.wsConnection.close(1000, 'Client disconnect');
      this.wsConnection = null;
    }

    this.listeners.clear();
  }

  /**
   * 모든 일정 목록 조회
   */
  async getEvents(): Promise<APIResponse<CalendarEvent[]>> {
    const response = await apiClient.get<CalendarEvent[]>(`${this.endpoint}/`);
    
    // 성공적으로 데이터를 받으면 타임스탬프 업데이트
    if (response.success) {
      this.lastSyncTimestamp = new Date().toISOString();
    }
    
    return response;
  }

  /**
   * 특정 일정 조회
   */
  async getEvent(id: number): Promise<APIResponse<CalendarEvent>> {
    return apiClient.get<CalendarEvent>(`${this.endpoint}/${id}/`);
  }

  /**
   * 새 일정 생성 (실시간 동기화 지원)
   */
  async createEvent(data: CreateCalendarEventData): Promise<APIResponse<CalendarEvent>> {
    const response = await apiClient.post<CalendarEvent>(`${this.endpoint}/`, data);
    
    // 성공 시 즉시 동기화 확인
    if (response.success) {
      setTimeout(() => this.checkForUpdates(), 100);
    }
    
    return response;
  }

  /**
   * 일정 전체 업데이트 (실시간 동기화 지원)
   */
  async updateEvent(id: number, data: CreateCalendarEventData): Promise<APIResponse<CalendarEvent>> {
    const response = await apiClient.put<CalendarEvent>(`${this.endpoint}/${id}/`, data);
    
    // 성공 시 즉시 동기화 확인
    if (response.success) {
      setTimeout(() => this.checkForUpdates(), 100);
    }
    
    return response;
  }

  /**
   * 일정 부분 업데이트 (실시간 동기화 지원)
   */
  async patchEvent(id: number, data: UpdateCalendarEventData): Promise<APIResponse<CalendarEvent>> {
    const response = await apiClient.patch<CalendarEvent>(`${this.endpoint}/${id}/`, data);
    
    // 성공 시 즉시 동기화 확인
    if (response.success) {
      setTimeout(() => this.checkForUpdates(), 100);
    }
    
    return response;
  }

  /**
   * 일정 삭제 (실시간 동기화 지원)
   */
  async deleteEvent(id: number): Promise<APIResponse<void>> {
    const response = await apiClient.delete<void>(`${this.endpoint}/${id}/`);
    
    // 성공 시 즉시 동기화 확인
    if (response.success) {
      setTimeout(() => this.checkForUpdates(), 100);
    }
    
    return response;
  }

  /**
   * 일정 일괄 업데이트 (드래그 앤 드롭 등)
   */
  async batchUpdateEvents(updates: Array<{id: number; data: UpdateCalendarEventData}>): Promise<APIResponse<CalendarEvent[]>> {
    const response = await apiClient.post<CalendarEvent[]>(`${this.endpoint}/batch-update/`, {
      updates
    });
    
    // 성공 시 즉시 동기화 확인
    if (response.success) {
      setTimeout(() => this.checkForUpdates(), 100);
    }
    
    return response;
  }

  /**
   * 날짜별 일정 조회
   */
  async getEventsByDate(date: string): Promise<APIResponse<CalendarEvent[]>> {
    return apiClient.get<CalendarEvent[]>(`${this.endpoint}/?date=${date}`);
  }

  /**
   * 날짜 범위별 일정 조회
   */
  async getEventsByDateRange(startDate: string, endDate: string): Promise<APIResponse<CalendarEvent[]>> {
    return apiClient.get<CalendarEvent[]>(`${this.endpoint}/?start_date=${startDate}&end_date=${endDate}`);
  }
}

// 싱글톤 인스턴스 export
export const calendarService = new CalendarService();