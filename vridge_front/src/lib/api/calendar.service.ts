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

//    
export interface CalendarUpdateEvent {
  type: 'create' | 'update' | 'delete' | 'bulk_update';
  event?: CalendarEvent;
  eventId?: number;
  events?: CalendarEvent[];
  timestamp: string;
}

//    
export type CalendarSyncListener = (update: CalendarUpdateEvent) => void;

/**
 * Calendar API  
 *      CRUD  .
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
  private reconnectDelay: number = 1000; // 1 

  constructor() {
    //     
    if (typeof window !== 'undefined') {
      window.addEventListener('beforeunload', this.cleanup.bind(this));
      window.addEventListener('visibilitychange', this.handleVisibilityChange.bind(this));
    }
  }

  /**
   *   
   */
  startRealTimeSync(): void {
    this.initializeWebSocket();
    this.startPolling();
  }

  /**
   *   
   */
  stopRealTimeSync(): void {
    this.cleanup();
  }

  /**
   *    
   */
  addSyncListener(listener: CalendarSyncListener): void {
    this.listeners.add(listener);
    
    //        
    if (this.listeners.size === 1) {
      this.startRealTimeSync();
    }
  }

  /**
   *    
   */
  removeSyncListener(listener: CalendarSyncListener): void {
    this.listeners.delete(listener);
    
    //      
    if (this.listeners.size === 0) {
      this.stopRealTimeSync();
    }
  }

  /**
   * WebSocket  
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
      console.warn('WebSocket   :', error);
      // WebSocket   polling 
      this.ensurePollingIsActive();
    }
  }

  /**
   * WebSocket   
   */
  private handleWebSocketOpen(): void {
    console.log(' WebSocket  ');
    this.reconnectAttempts = 0;
    this.reconnectDelay = 1000;
    
    // WebSocket    polling  
    if (this.isPollingActive) {
      this.restartPolling(30000); // 30 
    }
  }

  /**
   * WebSocket  
   */
  private handleWebSocketMessage(event: MessageEvent): void {
    try {
      const data = JSON.parse(event.data) as CalendarUpdateEvent;
      this.lastSyncTimestamp = data.timestamp;
      this.notifyListeners(data);
    } catch (error) {
      console.error('WebSocket   :', error);
    }
  }

  /**
   * WebSocket   
   */
  private handleWebSocketClose(event: CloseEvent): void {
    console.log(' WebSocket  :', event.code);
    this.wsConnection = null;

    //      
    if (event.code !== 1000 && this.listeners.size > 0) {
      this.attemptReconnection();
    }

    // WebSocket    polling 
    this.ensurePollingIsActive();
  }

  /**
   * WebSocket  
   */
  private handleWebSocketError(error: Event): void {
    console.error(' WebSocket :', error);
    this.ensurePollingIsActive();
  }

  /**
   * WebSocket  
   */
  private attemptReconnection(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.warn('WebSocket    ');
      return;
    }

    this.reconnectAttempts++;
    const delay = Math.min(this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1), 30000);

    setTimeout(() => {
      if (this.listeners.size > 0) {
        console.log(`WebSocket   ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
        this.initializeWebSocket();
      }
    }, delay);
  }

  /**
   * Polling 
   */
  private startPolling(): void {
    this.isPollingActive = true;
    this.restartPolling(5000); //  5 
  }

  /**
   * Polling 
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
   * Polling     
   */
  private ensurePollingIsActive(): void {
    if (!this.isPollingActive && this.listeners.size > 0) {
      this.startPolling();
    }
  }

  /**
   *    (Polling)
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
        
        //    
        response.data.updates.forEach(update => {
          this.notifyListeners(update);
        });
      }
    } catch (error) {
      console.error('    :', error);
    }
  }

  /**
   *   
   */
  private notifyListeners(update: CalendarUpdateEvent): void {
    this.listeners.forEach(listener => {
      try {
        listener(update);
      } catch (error) {
        console.error('    :', error);
      }
    });
  }

  /**
   *    
   */
  private handleVisibilityChange(): void {
    if (document.visibilityState === 'visible') {
      //      
      this.checkForUpdates();
      
      // WebSocket     
      if (!this.wsConnection || this.wsConnection.readyState !== WebSocket.OPEN) {
        this.initializeWebSocket();
      }
    }
  }

  /**
   *    
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
   *    
   */
  async getEvents(): Promise<APIResponse<CalendarEvent[]>> {
    const response = await apiClient.get<CalendarEvent[]>(`${this.endpoint}/`);
    
    //     
    if (response.success) {
      this.lastSyncTimestamp = new Date().toISOString();
    }
    
    return response;
  }

  /**
   *   
   */
  async getEvent(id: number): Promise<APIResponse<CalendarEvent>> {
    return apiClient.get<CalendarEvent>(`${this.endpoint}/${id}/`);
  }

  /**
   *    (  )
   */
  async createEvent(data: CreateCalendarEventData): Promise<APIResponse<CalendarEvent>> {
    const response = await apiClient.post<CalendarEvent>(`${this.endpoint}/`, data);
    
    //     
    if (response.success) {
      setTimeout(() => this.checkForUpdates(), 100);
    }
    
    return response;
  }

  /**
   *    (  )
   */
  async updateEvent(id: number, data: CreateCalendarEventData): Promise<APIResponse<CalendarEvent>> {
    const response = await apiClient.put<CalendarEvent>(`${this.endpoint}/${id}/`, data);
    
    //     
    if (response.success) {
      setTimeout(() => this.checkForUpdates(), 100);
    }
    
    return response;
  }

  /**
   *    (  )
   */
  async patchEvent(id: number, data: UpdateCalendarEventData): Promise<APIResponse<CalendarEvent>> {
    const response = await apiClient.patch<CalendarEvent>(`${this.endpoint}/${id}/`, data);
    
    //     
    if (response.success) {
      setTimeout(() => this.checkForUpdates(), 100);
    }
    
    return response;
  }

  /**
   *   (  )
   */
  async deleteEvent(id: number): Promise<APIResponse<void>> {
    const response = await apiClient.delete<void>(`${this.endpoint}/${id}/`);
    
    //     
    if (response.success) {
      setTimeout(() => this.checkForUpdates(), 100);
    }
    
    return response;
  }

  /**
   *    (   )
   */
  async batchUpdateEvents(updates: Array<{id: number; data: UpdateCalendarEventData}>): Promise<APIResponse<CalendarEvent[]>> {
    const response = await apiClient.post<CalendarEvent[]>(`${this.endpoint}/batch-update/`, {
      updates
    });
    
    //     
    if (response.success) {
      setTimeout(() => this.checkForUpdates(), 100);
    }
    
    return response;
  }

  /**
   *   
   */
  async getEventsByDate(date: string): Promise<APIResponse<CalendarEvent[]>> {
    return apiClient.get<CalendarEvent[]>(`${this.endpoint}/?date=${date}`);
  }

  /**
   *    
   */
  async getEventsByDateRange(startDate: string, endDate: string): Promise<APIResponse<CalendarEvent[]>> {
    return apiClient.get<CalendarEvent[]>(`${this.endpoint}/?start_date=${startDate}&end_date=${endDate}`);
  }
}

//   export
export const calendarService = new CalendarService();