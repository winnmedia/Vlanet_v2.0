'use client';

import { useState, useRef, useEffect } from 'react';
import { 
  MessageSquare, 
  Clock, 
  AlertCircle, 
  CheckCircle2, 
  XCircle, 
  Edit3, 
  Trash2, 
  Reply, 
  MoreHorizontal,
  Filter,
  Search,
  SortAsc,
  SortDesc,
  Tag,
  User
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import type { 
  TimelineFeedback, 
  FeedbackCategory, 
  FeedbackPriority, 
  FeedbackStatus, 
  User as UserType 
} from '@/types/video-feedback';

interface TimelineFeedbackProps {
  feedbacks: TimelineFeedback[];
  currentTime?: number;
  onFeedbackClick?: (feedback: TimelineFeedback) => void;
  onCreateFeedback?: (data: CreateFeedbackFormData) => void;
  onUpdateFeedback?: (id: string, data: Partial<TimelineFeedback>) => void;
  onDeleteFeedback?: (id: string) => void;
  onReplyToFeedback?: (feedbackId: string, content: string, mentions?: number[]) => void;
  mentionableUsers?: UserType[];
  className?: string;
}

interface CreateFeedbackFormData {
  timestamp: number;
  category: FeedbackCategory;
  priority: FeedbackPriority;
  title: string;
  content: string;
  mentions?: number[];
  tags?: string[];
}

interface FeedbackFilters {
  category?: FeedbackCategory | 'all';
  priority?: FeedbackPriority | 'all';
  status?: FeedbackStatus | 'all';
  author?: number | 'all';
  search?: string;
  sortBy: 'timestamp' | 'created_at' | 'priority';
  sortOrder: 'asc' | 'desc';
}

export default function TimelineFeedback({
  feedbacks,
  currentTime = 0,
  onFeedbackClick,
  onCreateFeedback,
  onUpdateFeedback,
  onDeleteFeedback,
  onReplyToFeedback,
  mentionableUsers = [],
  className = ''
}: TimelineFeedbackProps) {
  const [filters, setFilters] = useState<FeedbackFilters>({
    category: 'all',
    priority: 'all',
    status: 'all',
    author: 'all',
    search: '',
    sortBy: 'timestamp',
    sortOrder: 'asc'
  });

  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingFeedback, setEditingFeedback] = useState<TimelineFeedback | null>(null);
  const [replyingTo, setReplyingTo] = useState<string | null>(null);
  const [showFilters, setShowFilters] = useState(false);

  const [formData, setFormData] = useState<CreateFeedbackFormData>({
    timestamp: currentTime,
    category: 'general',
    priority: 'medium',
    title: '',
    content: '',
    mentions: [],
    tags: []
  });

  const [replyContent, setReplyContent] = useState('');

  //    
  const filteredAndSortedFeedbacks = feedbacks
    .filter(feedback => {
      if (filters.category !== 'all' && feedback.category !== filters.category) return false;
      if (filters.priority !== 'all' && feedback.priority !== filters.priority) return false;
      if (filters.status !== 'all' && feedback.status !== filters.status) return false;
      if (filters.author !== 'all' && feedback.author.id !== filters.author) return false;
      if (filters.search) {
        const searchLower = filters.search.toLowerCase();
        return (
          feedback.title.toLowerCase().includes(searchLower) ||
          feedback.content.toLowerCase().includes(searchLower) ||
          feedback.author.first_name.toLowerCase().includes(searchLower) ||
          feedback.author.last_name.toLowerCase().includes(searchLower)
        );
      }
      return true;
    })
    .sort((a, b) => {
      let comparison = 0;
      
      switch (filters.sortBy) {
        case 'timestamp':
          comparison = a.timestamp - b.timestamp;
          break;
        case 'created_at':
          comparison = new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
          break;
        case 'priority':
          const priorityOrder = { urgent: 4, high: 3, medium: 2, low: 1 };
          comparison = priorityOrder[b.priority] - priorityOrder[a.priority];
          break;
      }
      
      return filters.sortOrder === 'desc' ? -comparison : comparison;
    });

  //  
  const formatTime = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  //  
  const getCategoryIcon = (category: FeedbackCategory) => {
    const icons = {
      general: MessageSquare,
      correction: AlertCircle,
      question: MessageSquare,
      approval: CheckCircle2,
      suggestion: Edit3,
      technical: AlertCircle,
      creative: Edit3
    };
    const IconComponent = icons[category] || MessageSquare;
    return <IconComponent size={16} />;
  };

  //  
  const getCategoryColor = (category: FeedbackCategory): string => {
    const colors = {
      general: 'bg-gray-100 text-gray-700 border-gray-200',
      correction: 'bg-red-100 text-red-700 border-red-200',
      question: 'bg-blue-100 text-blue-700 border-blue-200',
      approval: 'bg-green-100 text-green-700 border-green-200',
      suggestion: 'bg-yellow-100 text-yellow-700 border-yellow-200',
      technical: 'bg-purple-100 text-purple-700 border-purple-200',
      creative: 'bg-pink-100 text-pink-700 border-pink-200'
    };
    return colors[category] || colors.general;
  };

  //  
  const getPriorityColor = (priority: FeedbackPriority): string => {
    const colors = {
      urgent: 'text-red-600 bg-red-50 border-red-200',
      high: 'text-orange-600 bg-orange-50 border-orange-200',
      medium: 'text-yellow-600 bg-yellow-50 border-yellow-200',
      low: 'text-green-600 bg-green-50 border-green-200'
    };
    return colors[priority];
  };

  //  
  const getStatusColor = (status: FeedbackStatus): string => {
    const colors = {
      active: 'text-blue-600 bg-blue-50 border-blue-200',
      resolved: 'text-green-600 bg-green-50 border-green-200',
      declined: 'text-gray-600 bg-gray-50 border-gray-200'
    };
    return colors[status];
  };

  //  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (editingFeedback) {
      onUpdateFeedback?.(editingFeedback.id, formData);
      setEditingFeedback(null);
    } else {
      onCreateFeedback?.(formData);
    }
    
    setShowCreateModal(false);
    resetForm();
  };

  //  
  const handleReplySubmit = (feedbackId: string) => {
    if (replyContent.trim()) {
      onReplyToFeedback?.(feedbackId, replyContent);
      setReplyContent('');
      setReplyingTo(null);
    }
  };

  //  
  const resetForm = () => {
    setFormData({
      timestamp: currentTime,
      category: 'general',
      priority: 'medium',
      title: '',
      content: '',
      mentions: [],
      tags: []
    });
  };

  //  
  const handleEdit = (feedback: TimelineFeedback) => {
    setEditingFeedback(feedback);
    setFormData({
      timestamp: feedback.timestamp,
      category: feedback.category,
      priority: feedback.priority,
      title: feedback.title,
      content: feedback.content,
      mentions: feedback.mentions || [],
      tags: feedback.tags || []
    });
    setShowCreateModal(true);
  };

  //      
  const isNearCurrentTime = (timestamp: number): boolean => {
    return Math.abs(timestamp - currentTime) < 2; // 2 
  };

  return (
    <div className={`flex flex-col h-full ${className}`}>
      {/*  */}
      <div className="flex items-center justify-between p-4 border-b">
        <h3 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
          <MessageSquare size={20} />
           ({filteredAndSortedFeedbacks.length})
        </h3>
        
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowFilters(!showFilters)}
            className={`${showFilters ? 'bg-blue-50 text-blue-600' : ''}`}
          >
            <Filter size={16} />
          </Button>
          
          <Button
            size="sm"
            onClick={() => setShowCreateModal(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white"
          >
             
          </Button>
        </div>
      </div>

      {/*   */}
      {showFilters && (
        <div className="p-4 bg-gray-50 border-b space-y-3">
          {/*  */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
            <input
              type="text"
              placeholder=" ..."
              value={filters.search}
              onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
              className="w-full pl-9 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/*   */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <select
              value={filters.category}
              onChange={(e) => setFilters(prev => ({ ...prev, category: e.target.value as any }))}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
            >
              <option value="all"> </option>
              <option value="general"></option>
              <option value="correction"></option>
              <option value="question"></option>
              <option value="approval"></option>
              <option value="suggestion"></option>
              <option value="technical"></option>
              <option value="creative"></option>
            </select>

            <select
              value={filters.priority}
              onChange={(e) => setFilters(prev => ({ ...prev, priority: e.target.value as any }))}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
            >
              <option value="all"> </option>
              <option value="urgent"></option>
              <option value="high"></option>
              <option value="medium"></option>
              <option value="low"></option>
            </select>

            <select
              value={filters.status}
              onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value as any }))}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
            >
              <option value="all"> </option>
              <option value="active"></option>
              <option value="resolved"></option>
              <option value="declined"></option>
            </select>

            <div className="flex">
              <select
                value={filters.sortBy}
                onChange={(e) => setFilters(prev => ({ ...prev, sortBy: e.target.value as any }))}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-l-lg text-sm"
              >
                <option value="timestamp"></option>
                <option value="created_at"></option>
                <option value="priority"></option>
              </select>
              <button
                onClick={() => setFilters(prev => ({ 
                  ...prev, 
                  sortOrder: prev.sortOrder === 'asc' ? 'desc' : 'asc' 
                }))}
                className="px-3 py-2 border border-l-0 border-gray-300 rounded-r-lg bg-gray-50 hover:bg-gray-100"
              >
                {filters.sortOrder === 'asc' ? <SortAsc size={16} /> : <SortDesc size={16} />}
              </button>
            </div>
          </div>
        </div>
      )}

      {/*   */}
      <div className="flex-1 overflow-y-auto">
        {filteredAndSortedFeedbacks.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <MessageSquare size={48} className="mb-4 opacity-50" />
            <p className="text-lg font-medium">  </p>
            <p className="text-sm">       .</p>
          </div>
        ) : (
          <div className="space-y-1">
            {filteredAndSortedFeedbacks.map((feedback) => (
              <div 
                key={feedback.id} 
                className={`p-4 border-b hover:bg-gray-50 cursor-pointer transition-colors ${
                  isNearCurrentTime(feedback.timestamp) ? 'bg-blue-50 border-blue-200' : ''
                }`}
                onClick={() => onFeedbackClick?.(feedback)}
              >
                {/*   */}
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2 flex-1">
                    <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium border ${getCategoryColor(feedback.category)}`}>
                      {getCategoryIcon(feedback.category)}
                      {feedback.category}
                    </div>
                    
                    <div className={`px-2 py-1 rounded-full text-xs font-medium border ${getPriorityColor(feedback.priority)}`}>
                      {feedback.priority}
                    </div>
                    
                    <div className={`px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(feedback.status)}`}>
                      {feedback.status}
                    </div>
                    
                    <div className="flex items-center gap-1 text-xs text-gray-500">
                      <Clock size={12} />
                      {formatTime(feedback.timestamp)}
                    </div>
                  </div>

                  <div className="flex items-center gap-1">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleEdit(feedback);
                      }}
                      className="p-1 hover:bg-gray-200 rounded transition-colors"
                    >
                      <Edit3 size={14} />
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onDeleteFeedback?.(feedback.id);
                      }}
                      className="p-1 hover:bg-gray-200 rounded transition-colors text-red-600"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>

                {/*   */}
                <h4 className="font-medium text-gray-800 mb-1">{feedback.title}</h4>
                <p className="text-gray-600 text-sm mb-2">{feedback.content}</p>

                {/*    */}
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <div className="flex items-center gap-2">
                    <User size={12} />
                    {feedback.author.first_name} {feedback.author.last_name}
                    <span>•</span>
                    {new Date(feedback.created_at).toLocaleDateString()}
                  </div>
                  
                  {feedback.replies && feedback.replies.length > 0 && (
                    <div className="flex items-center gap-1">
                      <Reply size={12} />
                      {feedback.replies.length}
                    </div>
                  )}
                </div>

                {/*  */}
                {feedback.replies && feedback.replies.length > 0 && (
                  <div className="mt-3 ml-4 space-y-2 border-l-2 border-gray-200 pl-3">
                    {feedback.replies.map((reply) => (
                      <div key={reply.id} className="text-sm">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-medium text-gray-700">
                            {reply.author.first_name} {reply.author.last_name}
                          </span>
                          <span className="text-xs text-gray-500">
                            {new Date(reply.created_at).toLocaleDateString()}
                          </span>
                        </div>
                        <p className="text-gray-600">{reply.content}</p>
                      </div>
                    ))}
                  </div>
                )}

                {/*   */}
                {replyingTo === feedback.id ? (
                  <div className="mt-3 flex gap-2">
                    <input
                      type="text"
                      value={replyContent}
                      onChange={(e) => setReplyContent(e.target.value)}
                      placeholder=" ..."
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                          handleReplySubmit(feedback.id);
                        } else if (e.key === 'Escape') {
                          setReplyingTo(null);
                          setReplyContent('');
                        }
                      }}
                    />
                    <Button
                      size="sm"
                      onClick={() => handleReplySubmit(feedback.id)}
                      disabled={!replyContent.trim()}
                    >
                      
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        setReplyingTo(null);
                        setReplyContent('');
                      }}
                    >
                      
                    </Button>
                  </div>
                ) : (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setReplyingTo(feedback.id);
                    }}
                    className="mt-2 text-xs text-blue-600 hover:text-blue-700 flex items-center gap-1"
                  >
                    <Reply size={12} />
                     
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/*  /  */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => {
          setShowCreateModal(false);
          setEditingFeedback(null);
          resetForm();
        }}
        title={editingFeedback ? ' ' : '  '}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                
              </label>
              <div className="flex items-center gap-2">
                <input
                  type="number"
                  step="0.1"
                  value={formData.timestamp}
                  onChange={(e) => setFormData(prev => ({ ...prev, timestamp: parseFloat(e.target.value) || 0 }))}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => setFormData(prev => ({ ...prev, timestamp: currentTime }))}
                >
                   
                </Button>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                
              </label>
              <select
                value={formData.category}
                onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value as FeedbackCategory }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="general"></option>
                <option value="correction"></option>
                <option value="question"></option>
                <option value="approval"></option>
                <option value="suggestion"></option>
                <option value="technical"></option>
                <option value="creative"></option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              
            </label>
            <select
              value={formData.priority}
              onChange={(e) => setFormData(prev => ({ ...prev, priority: e.target.value as FeedbackPriority }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="low"></option>
              <option value="medium"></option>
              <option value="high"></option>
              <option value="urgent"></option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
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
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="  "
            />
          </div>

          <div className="flex gap-3 pt-4">
            <Button
              type="submit"
              className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
            >
              {editingFeedback ? '' : ''}
            </Button>
            <Button
              type="button"
              variant="ghost"
              onClick={() => {
                setShowCreateModal(false);
                setEditingFeedback(null);
                resetForm();
              }}
              className="flex-1 border border-gray-300 hover:bg-gray-50"
            >
              
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}