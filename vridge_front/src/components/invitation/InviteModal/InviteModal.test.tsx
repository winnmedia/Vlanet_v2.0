import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { InviteModal } from './InviteModal'
import { useToast } from '@/contexts/toast.context'

// Mock dependencies
vi.mock('@/contexts/toast.context', () => ({
  useToast: vi.fn(() => ({
    success: vi.fn(),
    error: vi.fn()
  }))
}))

vi.mock('@/lib/api/invitation.service', () => ({
  invitationService: {
    getFriends: vi.fn().mockResolvedValue({
      success: true,
      data: [
        {
          id: 1,
          name: 'John Doe',
          email: 'john@example.com',
          added_at: '2024-01-01T00:00:00Z',
          last_interaction: '2024-01-01T00:00:00Z',
          projects_shared: 2
        }
      ]
    }),
    sendInvitation: vi.fn().mockResolvedValue({
      success: true,
      data: { id: 1 }
    })
  }
}))

describe('InviteModal Component', () => {
  const defaultProps = {
    isOpen: true,
    onClose: vi.fn(),
    onInviteSent: vi.fn()
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders modal when open', () => {
    render(<InviteModal {...defaultProps} />)

    expect(screen.getByText(' ')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('  ...')).toBeInTheDocument()
  })

  it('does not render when closed', () => {
    render(<InviteModal {...defaultProps} isOpen={false} />)

    expect(screen.queryByText(' ')).not.toBeInTheDocument()
  })

  it('shows project information when projectTitle is provided', () => {
    render(
      <InviteModal 
        {...defaultProps} 
        projectTitle="Test Project"
        projectId={1}
      />
    )

    expect(screen.getByText('Test Project ')).toBeInTheDocument()
    expect(screen.getByText(': Test Project')).toBeInTheDocument()
  })

  it('allows adding custom email', async () => {
    render(<InviteModal {...defaultProps} />)

    const emailInput = screen.getByPlaceholderText('example@email.com')
    const addButton = screen.getByText('')

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
    fireEvent.click(addButton)

    await waitFor(() => {
      expect(screen.getByText('test@example.com')).toBeInTheDocument()
    })
  })

  it('validates email format', async () => {
    const mockError = vi.fn()
    vi.mocked(useToast).mockReturnValue({
      success: vi.fn(),
      error: mockError
    })

    render(<InviteModal {...defaultProps} />)

    const emailInput = screen.getByPlaceholderText('example@email.com')
    const addButton = screen.getByText('')

    fireEvent.change(emailInput, { target: { value: 'invalid-email' } })
    fireEvent.click(addButton)

    await waitFor(() => {
      expect(mockError).toHaveBeenCalledWith('   .')
    })
  })

  it('allows adding invitation message', () => {
    render(<InviteModal {...defaultProps} />)

    const messageTextarea = screen.getByPlaceholderText('   !')

    fireEvent.change(messageTextarea, { target: { value: 'Custom invitation message' } })

    expect(messageTextarea).toHaveValue('Custom invitation message')
  })

  it('disables send button when no emails selected', () => {
    render(<InviteModal {...defaultProps} />)

    const sendButton = screen.getByText(/ /)

    expect(sendButton).toBeDisabled()
  })

  it('calls onClose when cancel button is clicked', () => {
    const mockOnClose = vi.fn()

    render(<InviteModal {...defaultProps} onClose={mockOnClose} />)

    const cancelButton = screen.getByText('')
    fireEvent.click(cancelButton)

    expect(mockOnClose).toHaveBeenCalled()
  })
})