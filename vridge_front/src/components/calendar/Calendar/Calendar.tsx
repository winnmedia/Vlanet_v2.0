'use client'

import { useState, useCallback, useRef, useEffect } from 'react'
import FullCalendar from '@fullcalendar/react'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import interactionPlugin from '@fullcalendar/interaction'
import { EventInput, DateSelectArg, EventClickArg, EventDropArg } from '@fullcalendar/core'
import { Button } from '@/components/ui/Button'
import { useToast } from '@/contexts/toast.context'
import { 
  CalendarEvent, 
  CalendarUpdateEvent, 
  CalendarSyncListener, 
  calendarService 
} from '@/lib/api/calendar.service'

export interface CalendarProps {
  events: CalendarEvent[]
  onEventCreate?: (dateInfo: DateSelectArg) => void
  onEventEdit?: (event: CalendarEvent) => void
  onEventDelete?: (eventId: number) => void
  onEventUpdate?: (eventId: number, dateInfo: EventDropArg) => void
  onEventsUpdated?: (events: CalendarEvent[]) => void
  isLoading?: boolean
  enableRealTimeSync?: boolean
}

const Calendar = ({
  events = [],
  onEventCreate,
  onEventEdit,
  onEventDelete,
  onEventUpdate,
  onEventsUpdated,
  isLoading = false,
  enableRealTimeSync = true
}: CalendarProps) => {
  const { success, error } = useToast()
  const [currentView, setCurrentView] = useState<'dayGridMonth' | 'timeGridWeek' | 'timeGridDay'>('dayGridMonth')
  const [localEvents, setLocalEvents] = useState<CalendarEvent[]>(events)
  const [syncStatus, setSyncStatus] = useState<'connected' | 'disconnected' | 'syncing'>('disconnected')
  const calendarRef = useRef<FullCalendar>(null)

  //   
  useEffect(() => {
    if (!enableRealTimeSync) return;

    const handleSyncUpdate: CalendarSyncListener = (update: CalendarUpdateEvent) => {
      setSyncStatus('syncing');
      
      switch (update.type) {
        case 'create':
          if (update.event) {
            setLocalEvents(prev => {
              const exists = prev.find(e => e.id === update.event!.id);
              if (!exists) {
                const newEvents = [...prev, update.event!];
                onEventsUpdated?.(newEvents);
                return newEvents;
              }
              return prev;
            });
            success(`  : ${update.event.title}`);
          }
          break;

        case 'update':
          if (update.event) {
            setLocalEvents(prev => {
              const newEvents = prev.map(e => 
                e.id === update.event!.id ? update.event! : e
              );
              onEventsUpdated?.(newEvents);
              return newEvents;
            });
            success(` : ${update.event.title}`);
          }
          break;

        case 'delete':
          if (update.eventId) {
            setLocalEvents(prev => {
              const deletedEvent = prev.find(e => e.id === update.eventId);
              const newEvents = prev.filter(e => e.id !== update.eventId);
              onEventsUpdated?.(newEvents);
              if (deletedEvent) {
                success(` : ${deletedEvent.title}`);
              }
              return newEvents;
            });
          }
          break;

        case 'bulk_update':
          if (update.events) {
            setLocalEvents(update.events);
            onEventsUpdated?.(update.events);
            success('  .');
          }
          break;
      }

      //      
      setTimeout(() => setSyncStatus('connected'), 500);
    };

    //   
    calendarService.addSyncListener(handleSyncUpdate);
    setSyncStatus('connected');

    return () => {
      calendarService.removeSyncListener(handleSyncUpdate);
      setSyncStatus('disconnected');
    };
  }, [enableRealTimeSync, onEventsUpdated, success]);

  //      
  useEffect(() => {
    setLocalEvents(events);
  }, [events]);

  //    (      )
  const displayEvents = enableRealTimeSync ? localEvents : events;

  //    
  const calendarEvents: EventInput[] = displayEvents.map((event) => ({
    id: event.id.toString(),
    title: event.title,
    start: `${event.date}T${event.time}`,
    extendedProps: {
      description: event.description,
      originalEvent: event
    },
    backgroundColor: getEventColor(event),
    borderColor: getEventColor(event)
  }))

  //    (   )
  function getEventColor(event: CalendarEvent): string {
    //    
    const eventDate = new Date(`${event.date}T${event.time}`)
    const today = new Date()
    
    if (eventDate < today) {
      return '#ef4444' //   ()
    }
    
    //   (24 )
    const diffHours = (eventDate.getTime() - today.getTime()) / (1000 * 60 * 60)
    if (diffHours <= 24 && diffHours > 0) {
      return '#f59e0b' //   ()
    }
    
    return '#3b82f6' //   ()
  }

  //      
  const handleDateSelect = useCallback((selectInfo: DateSelectArg) => {
    if (onEventCreate) {
      onEventCreate(selectInfo)
    }
  }, [onEventCreate])

  //    
  const handleEventClick = useCallback((clickInfo: EventClickArg) => {
    const originalEvent = clickInfo.event.extendedProps.originalEvent as CalendarEvent
    if (onEventEdit) {
      onEventEdit(originalEvent)
    }
  }, [onEventEdit])

  //     / 
  const handleEventDrop = useCallback((dropInfo: EventDropArg) => {
    if (onEventUpdate) {
      const eventId = parseInt(dropInfo.event.id)
      onEventUpdate(eventId, dropInfo)
    }
  }, [onEventUpdate])

  //   
  const handleViewChange = (view: 'dayGridMonth' | 'timeGridWeek' | 'timeGridDay') => {
    setCurrentView(view)
    const calendarApi = calendarRef.current?.getApi()
    if (calendarApi) {
      calendarApi.changeView(view)
    }
  }

  //  
  const goToToday = () => {
    const calendarApi = calendarRef.current?.getApi()
    if (calendarApi) {
      calendarApi.today()
    }
  }

  // / 
  const goToPrev = () => {
    const calendarApi = calendarRef.current?.getApi()
    if (calendarApi) {
      calendarApi.prev()
    }
  }

  const goToNext = () => {
    const calendarApi = calendarRef.current?.getApi()
    if (calendarApi) {
      calendarApi.next()
    }
  }

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-lg">
      {/*   */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex flex-wrap items-center justify-between gap-4">
          {/*   */}
          <div className="flex items-center space-x-2">
            <Button 
              onClick={goToPrev}
              variant="ghost"
              className="p-2 hover:bg-gray-100"
            >
              
            </Button>
            <Button 
              onClick={goToToday}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 text-sm"
            >
              
            </Button>
            <Button 
              onClick={goToNext}
              variant="ghost"
              className="p-2 hover:bg-gray-100"
            >
              
            </Button>
          </div>

          {/*    */}
          <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
            <Button
              onClick={() => handleViewChange('dayGridMonth')}
              className={`px-3 py-2 text-sm transition-colors ${
                currentView === 'dayGridMonth'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
              variant="ghost"
            >
              
            </Button>
            <Button
              onClick={() => handleViewChange('timeGridWeek')}
              className={`px-3 py-2 text-sm transition-colors ${
                currentView === 'timeGridWeek'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
              variant="ghost"
            >
              
            </Button>
            <Button
              onClick={() => handleViewChange('timeGridDay')}
              className={`px-3 py-2 text-sm transition-colors ${
                currentView === 'timeGridDay'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
              variant="ghost"
            >
              
            </Button>
          </div>
        </div>

        {/*     */}
        <div className="flex items-center justify-between mt-3">
          <div className="flex items-center space-x-4 text-sm">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-blue-500 rounded"></div>
              <span className="text-gray-600"></span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-orange-500 rounded"></div>
              <span className="text-gray-600"></span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-red-500 rounded"></div>
              <span className="text-gray-600"></span>
            </div>
          </div>

          {/*     */}
          {enableRealTimeSync && (
            <div className="flex items-center space-x-2 text-sm">
              <div className={`w-2 h-2 rounded-full ${
                syncStatus === 'connected' ? 'bg-green-500' :
                syncStatus === 'syncing' ? 'bg-yellow-500 animate-pulse' :
                'bg-red-500'
              }`}></div>
              <span className={`text-xs ${
                syncStatus === 'connected' ? 'text-green-600' :
                syncStatus === 'syncing' ? 'text-yellow-600' :
                'text-red-600'
              }`}>
                {syncStatus === 'connected' ? ' ' :
                 syncStatus === 'syncing' ? ' ...' :
                 ' '}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* FullCalendar */}
      <div className="p-4">
        <FullCalendar
          ref={calendarRef}
          plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
          initialView={currentView}
          headerToolbar={false}
          height="auto"
          locale="ko"
          selectable={true}
          selectMirror={true}
          editable={true}
          droppable={true}
          events={calendarEvents}
          select={handleDateSelect}
          eventClick={handleEventClick}
          eventDrop={handleEventDrop}
          weekends={true}
          dayMaxEvents={true}
          eventTextColor="white"
          eventDisplay="block"
          displayEventTime={true}
          eventTimeFormat={{
            hour: 'numeric',
            minute: '2-digit',
            meridiem: false
          }}
          slotLabelFormat={{
            hour: 'numeric',
            minute: '2-digit',
            meridiem: false
          }}
          buttonText={{
            today: '',
            month: '',
            week: '',
            day: ''
          }}
          noEventsText="  "
        />
      </div>
    </div>
  )
}

export default Calendar