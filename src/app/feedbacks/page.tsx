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

  // API 서비스 함수들
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
      error('피드백을 불러오는데 실패했습니다.')
    } finally {
      setIsLoading(false)
    }
  }

  const createFeedback = async (feedbackData: FeedbackFormData) => {
    try {
      const result = await feedbackService.createFeedback(feedbackData)
      if (result.success && result.data) {
        setFeedbacks(prev => [...prev, result.data])
        success('피드백이 생성되었습니다.')
      } else {
        throw new Error(result.error?.message || 'Failed to create feedback')
      }
    } catch (error) {
      console.error('Error creating feedback:', error)
      error('피드백 생성에 실패했습니다.')
    }
  }

  const updateFeedback = async (id: number, feedbackData: Partial<Feedback>) => {
    try {
      const result = await feedbackService.patchFeedback(id, feedbackData)
      if (result.success && result.data) {
        setFeedbacks(prev => prev.map(feedback => 
          feedback.id === id ? result.data : feedback
        ))
        success('피드백이 수정되었습니다.')
      } else {
        throw new Error(result.error?.message || 'Failed to update feedback')
      }
    } catch (error) {
      console.error('Error updating feedback:', error)
      error('피드백 수정에 실패했습니다.')
    }
  }

  const deleteFeedback = async (id: number) => {
    try {
      const result = await feedbackService.deleteFeedback(id)
      if (result.success) {
        setFeedbacks(prev => prev.filter(feedback => feedback.id !== id))
        success('피드백이 삭제되었습니다.')
      } else {
        throw new Error(result.error?.message || 'Failed to delete feedback')
      }
    } catch (error) {
      console.error('Error deleting feedback:', error)
      error('피드백 삭제에 실패했습니다.')
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
    if (window.confirm('정말로 이 피드백을 삭제하시겠습니까?')) {
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
      case 'pending': return '대기중'
      case 'in_progress': return '진행중'
      case 'resolved': return '해결됨'
      default: return status
    }
  }

  const getPriorityText = (priority: string) => {
    switch (priority) {
      case 'high': return '높음'
      case 'medium': return '보통'
      case 'low': return '낮음'
      default: return priority
    }
  }

  return (
    <DashboardLayout>
      <div className="p-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-800">피드백 관리</h1>
          <Button 
            onClick={() => setShowModal(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
          >
            새 피드백 추가
          </Button>
        </div>

        {/* 필터 버튼들 */}
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
              {status === 'all' ? '전체' : 
               status === 'pending' ? '대기중' :
               status === 'in_progress' ? '진행중' : '해결됨'}
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
                  ? '아직 등록된 피드백이 없습니다. 새 피드백을 추가해보세요.'
                  : `${getStatusText(filter)} 상태의 피드백이 없습니다.`
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
                          <span className="mr-4">📂 {feedback.category}</span>
                          <span>📅 {new Date(feedback.created_at).toLocaleDateString('ko-KR')}</span>
                        </div>
                      </div>
                      <div className="flex flex-col space-y-2">
                        <div className="flex space-x-2">
                          <Button
                            onClick={() => handleEdit(feedback)}
                            className="text-blue-600 hover:bg-blue-50 px-3 py-1 text-sm"
                            variant="ghost"
                          >
                            수정
                          </Button>
                          <Button
                            onClick={() => handleDelete(feedback.id)}
                            className="text-red-600 hover:bg-red-50 px-3 py-1 text-sm"
                            variant="ghost"
                          >
                            삭제
                          </Button>
                        </div>
                        <select
                          value={feedback.status}
                          onChange={(e) => handleStatusChange(feedback.id, e.target.value as any)}
                          className="text-xs border border-gray-300 rounded px-2 py-1"
                        >
                          <option value="pending">대기중</option>
                          <option value="in_progress">진행중</option>
                          <option value="resolved">해결됨</option>
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
          title={editingFeedback ? '피드백 수정' : '새 피드백 추가'}
        >
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                제목
              </label>
              <Input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                required
                className="w-full"
                placeholder="피드백 제목을 입력하세요"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                내용
              </label>
              <textarea
                value={formData.content}
                onChange={(e) => setFormData(prev => ({ ...prev, content: e.target.value }))}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                rows={4}
                placeholder="피드백 내용을 입력하세요"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                카테고리
              </label>
              <select
                value={formData.category}
                onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="general">일반</option>
                <option value="bug">버그</option>
                <option value="feature">기능 요청</option>
                <option value="improvement">개선 사항</option>
                <option value="ui_ux">UI/UX</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                우선순위
              </label>
              <select
                value={formData.priority}
                onChange={(e) => setFormData(prev => ({ ...prev, priority: e.target.value as any }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="low">낮음</option>
                <option value="medium">보통</option>
                <option value="high">높음</option>
              </select>
            </div>
            
            <div className="flex space-x-3 pt-4">
              <Button
                type="submit"
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg"
              >
                {editingFeedback ? '수정하기' : '추가하기'}
              </Button>
              <Button
                type="button"
                onClick={resetForm}
                variant="ghost"
                className="flex-1 border border-gray-300 hover:bg-gray-50 py-2 rounded-lg"
              >
                취소
              </Button>
            </div>
          </form>
        </Modal>
      </div>
    </DashboardLayout>
  )
}

export default FeedbackPage