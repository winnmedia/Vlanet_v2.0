import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { Calendar } from './Calendar'
import type { CalendarEvent } from '@/lib/api/calendar.service'

// Mock FullCalendar components
vi.mock('@fullcalendar/react', () => ({
  default: vi.fn(({ events, select, eventClick, eventDrop }) => (
    <div data-testid="fullcalendar">
      <div>Mock FullCalendar</div>
      <button 
        onClick={() => select && select({ startStr: '2024-01-15T10:00' })}
        data-testid="mock-date-select"
      >
        Select Date
      </button>
      {events?.map((event: any) => (
        <div key={event.id} data-testid={`event-${event.id}`}>
          <button 
            onClick={() => eventClick && eventClick({ event: { id: event.id, extendedProps: event.extendedProps } })}
          >
            {event.title}
          </button>
        </div>
      ))}
    </div>
  ))
}))

vi.mock('@fullcalendar/daygrid', () => ({}))
vi.mock('@fullcalendar/timegrid', () => ({}))
vi.mock('@fullcalendar/interaction', () => ({}))

const mockEvents: CalendarEvent[] = [
  {
    id: 1,
    title: 'Test Event 1',
    description: 'Test Description 1',
    date: '2024-01-15',
    time: '10:00',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z'
  },
  {
    id: 2,
    title: 'Test Event 2',
    description: 'Test Description 2',
    date: '2024-01-16',
    time: '14:00',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z'
  }
]

describe('Calendar Component', () => {
  it('renders calendar with events', () => {
    const mockOnEventCreate = vi.fn()
    const mockOnEventEdit = vi.fn()
    const mockOnEventDelete = vi.fn()

    render(
      <Calendar
        events={mockEvents}
        onEventCreate={mockOnEventCreate}
        onEventEdit={mockOnEventEdit}
        onEventDelete={mockOnEventDelete}
      />
    )

    expect(screen.getByTestId('fullcalendar')).toBeInTheDocument()
    expect(screen.getByText('Mock FullCalendar')).toBeInTheDocument()
  })

  it('shows loading state', () => {
    render(
      <Calendar
        events={[]}
        isLoading={true}
      />
    )

    expect(screen.getByRole('progressbar', { hidden: true })).toBeInTheDocument()
  })

  it('handles view changes', () => {
    render(
      <Calendar
        events={mockEvents}
      />
    )

    const weekButton = screen.getByText('')
    const dayButton = screen.getByText('')

    fireEvent.click(weekButton)
    fireEvent.click(dayButton)

    expect(weekButton).toBeInTheDocument()
    expect(dayButton).toBeInTheDocument()
  })

  it('calls onEventCreate when date is selected', () => {
    const mockOnEventCreate = vi.fn()

    render(
      <Calendar
        events={mockEvents}
        onEventCreate={mockOnEventCreate}
      />
    )

    const selectButton = screen.getByTestId('mock-date-select')
    fireEvent.click(selectButton)

    expect(mockOnEventCreate).toHaveBeenCalledWith({ startStr: '2024-01-15T10:00' })
  })

  it('displays navigation buttons', () => {
    render(
      <Calendar
        events={mockEvents}
      />
    )

    expect(screen.getByText('')).toBeInTheDocument()
    expect(screen.getByText('')).toBeInTheDocument()
    expect(screen.getByText('')).toBeInTheDocument()
  })

  it('displays priority legend', () => {
    render(
      <Calendar
        events={mockEvents}
      />
    )

    expect(screen.getByText('')).toBeInTheDocument()
    expect(screen.getByText('')).toBeInTheDocument()
    expect(screen.getByText('')).toBeInTheDocument()
  })
})