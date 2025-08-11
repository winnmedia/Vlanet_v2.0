'use client'

import { useState, useEffect } from 'react'
import DashboardLayout from '@/components/layout/DashboardLayout'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Modal } from '@/components/ui/Modal'
import { useToast } from '@/contexts/toast.context'
import { feedbackService, type Feedback, type CreateFeedbackData } from '@/lib/api/feedback.service'

interface FeedbackFormData extends CreateFeedbackData {}

const FeedbackPage = () => {
  const { success, error } = useToast()
  const [feedbacks, setFeedbacks] = useState<Feedback[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editingFeedback, setEditingFeedback] = useState<Feedback | null>(null)
  const [filter, setFilter] = useState<string>('all')
  const [formData, setFormData] = useState<FeedbackFormData>({
    title: '',
    content: '',
    category: 'general',
    priority: 'medium'
  })

  // API  
  const fetchFeedbacks = async () => {
    try {
      const result = await feedbackService.getFeedbacks()
      if (result.success && result.data) {
        setFeedbacks(result.data)
      } else {
        throw new Error(result.error?.message || 'Failed to fetch feedbacks')
      }
    } catch (error) {
      console.error('Error fetching feedbacks:', error)
      error('  .')
    } finally {
      setIsLoading(false)
    }
  }

  const createFeedback = async (feedbackData: FeedbackFormData) => {
    try {
      const result = await feedbackService.createFeedback(feedbackData)
      if (result.success && result.data) {
        setFeedbacks(prev => [...prev, result.data])
        success(' .')
      } else {
        throw new Error(result.error?.message || 'Failed to create feedback')
      }
    } catch (error) {
      console.error('Error creating feedback:', error)
      error('  .')
    }
  }

  const updateFeedback = async (id: number, feedbackData: Partial<Feedback>) => {
    try {
      const result = await feedbackService.patchFeedback(id, feedbackData)
      if (result.success && result.data) {
        setFeedbacks(prev => prev.map(feedback => 
          feedback.id === id ? result.data : feedback
        ))
        success(' .')
      } else {
        throw new Error(result.error?.message || 'Failed to update feedback')
      }
    } catch (error) {
      console.error('Error updating feedback:', error)
      error('  .')
    }
  }

  const deleteFeedback = async (id: number) => {
    try {
      const result = await feedbackService.deleteFeedback(id)
      if (result.success) {
        setFeedbacks(prev => prev.filter(feedback => feedback.id !== id))
        success(' .')
      } else {
        throw new Error(result.error?.message || 'Failed to delete feedback')
      }
    } catch (error) {
      console.error('Error deleting feedback:', error)
      error('  .')
    }
  }

  useEffect(() => {
    fetchFeedbacks()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (editingFeedback) {
      await updateFeedback(editingFeedback.id, formData)
    } else {
      await createFeedback(formData)
    }
    
    setShowModal(false)
    setEditingFeedback(null)
    setFormData({ title: '', content: '', category: 'general', priority: 'medium' })
  }

  const handleEdit = (feedback: Feedback) => {
    setEditingFeedback(feedback)
    setFormData({
      title: feedback.title,
      content: feedback.content,
      category: feedback.category,
      priority: feedback.priority
    })
    setShowModal(true)
  }

  const handleDelete = (id: number) => {
    if (window.confirm('   ?')) {
      deleteFeedback(id)
    }
  }

  const handleStatusChange = async (id: number, newStatus: 'pending' | 'in_progress' | 'resolved') => {
    await updateFeedback(id, { status: newStatus })
  }

  const resetForm = () => {
    setFormData({ title: '', content: '', category: 'general', priority: 'medium' })
    setEditingFeedback(null)
    setShowModal(false)
  }

  const filteredFeedbacks = feedbacks.filter(feedback => {
    if (filter === 'all') return true
    return feedback.status === filter
  })

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'text-red-600 bg-red-100'
      case 'medium': return 'text-yellow-600 bg-yellow-100'
      case 'low': return 'text-green-600 bg-green-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'text-gray-600 bg-gray-100'
      case 'in_progress': return 'text-blue-600 bg-blue-100'
      case 'resolved': return 'text-green-600 bg-green-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'pending': return ''
      case 'in_progress': return ''
      case 'resolved': return ''
      default: return status
    }
  }

  const getPriorityText = (priority: string) => {
    switch (priority) {
      case 'high': return ''
      case 'medium': return ''
      case 'low': return ''
      default: return priority
    }
  }

  return (
    <DashboardLayout>
      <div className="p-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-800"> </h1>
          <Button 
            onClick={() => setShowModal(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
          >
              
          </Button>
        </div>

        {/*   */}
        <div className="mb-4 flex space-x-2">
          {['all', 'pending', 'in_progress', 'resolved'].map((status) => (
            <Button
              key={status}
              onClick={() => setFilter(status)}
              variant={filter === status ? 'default' : 'ghost'}
              className={`px-4 py-2 rounded-lg ${
                filter === status 
                  ? 'bg-blue-600 text-white' 
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              {status === 'all' ? '' : 
               status === 'pending' ? '' :
               status === 'in_progress' ? '' : ''}
            </Button>
          ))}
        </div>

        {isLoading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow">
            {filteredFeedbacks.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                {filter === 'all' 
                  ? '   .   .'
                  : `${getStatusText(filter)}   .`
                }
              </div>
            ) : (
              <div className="divide-y divide-gray-200">
                {filteredFeedbacks.map((feedback) => (
                  <div key={feedback.id} className="p-4 hover:bg-gray-50">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <h3 className="text-lg font-semibold text-gray-800">
                            {feedback.title}
                          </h3>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(feedback.priority)}`}>
                            {getPriorityText(feedback.priority)}
                          </span>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(feedback.status)}`}>
                            {getStatusText(feedback.status)}
                          </span>
                        </div>
                        <p className="text-gray-600 mb-2">{feedback.content}</p>
                        <div className="flex items-center text-sm text-gray-500">
                          <span className="mr-4"> {feedback.category}</span>
                          <span> {new Date(feedback.created_at).toLocaleDateString('ko-KR')}</span>
                        </div>
                      </div>
                      <div className="flex flex-col space-y-2">
                        <div className="flex space-x-2">
                          <Button
                            onClick={() => handleEdit(feedback)}
                            className="text-blue-600 hover:bg-blue-50 px-3 py-1 text-sm"
                            variant="ghost"
                          >
                            
                          </Button>
                          <Button
                            onClick={() => handleDelete(feedback.id)}
                            className="text-red-600 hover:bg-red-50 px-3 py-1 text-sm"
                            variant="ghost"
                          >
                            
                          </Button>
                        </div>
                        <select
                          value={feedback.status}
                          onChange={(e) => handleStatusChange(feedback.id, e.target.value as any)}
                          className="text-xs border border-gray-300 rounded px-2 py-1"
                        >
                          <option value="pending"></option>
                          <option value="in_progress"></option>
                          <option value="resolved"></option>
                        </select>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        <Modal
          isOpen={showModal}
          onClose={resetForm}
          title={editingFeedback ? ' ' : '  '}
        >
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                
              </label>
              <Input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                required
                className="w-full"
                placeholder="  "
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                
              </label>
              <textarea
                value={formData.content}
                onChange={(e) => setFormData(prev => ({ ...prev, content: e.target.value }))}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                rows={4}
                placeholder="  "
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                
              </label>
              <select
                value={formData.category}
                onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="general"></option>
                <option value="bug"></option>
                <option value="feature"> </option>
                <option value="improvement"> </option>
                <option value="ui_ux">UI/UX</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                
              </label>
              <select
                value={formData.priority}
                onChange={(e) => setFormData(prev => ({ ...prev, priority: e.target.value as any }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="low"></option>
                <option value="medium"></option>
                <option value="high"></option>
              </select>
            </div>
            
            <div className="flex space-x-3 pt-4">
              <Button
                type="submit"
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg"
              >
                {editingFeedback ? '' : ''}
              </Button>
              <Button
                type="button"
                onClick={resetForm}
                variant="ghost"
                className="flex-1 border border-gray-300 hover:bg-gray-50 py-2 rounded-lg"
              >
                
              </Button>
            </div>
          </form>
        </Modal>
      </div>
    </DashboardLayout>
  )
}

export default FeedbackPage