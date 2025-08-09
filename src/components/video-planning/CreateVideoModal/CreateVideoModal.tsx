'use client';

import React, { useState } from 'react';
import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

interface VideoPlan {
  title: string;
  description: string;
  status: 'draft' | 'in_progress' | 'completed';
  category: string;
  duration: string;
  target_audience: string;
}

interface CreateVideoModalProps {
  onClose: () => void;
  onSubmit: (video: VideoPlan) => void;
}

const categoryOptions = [
  '브랜딩',
  '제품',
  '교육',
  '홍보',
  '이벤트',
  '인터뷰',
  '기타'
];

const statusOptions = [
  { value: 'draft', label: '초안' },
  { value: 'in_progress', label: '진행 중' },
  { value: 'completed', label: '완료' }
];

const durationOptions = [
  '30초',
  '1분',
  '2분',
  '3분',
  '5분',
  '10분',
  '15분',
  '30분',
  '사용자 정의'
];

const audienceOptions = [
  '잠재 고객',
  '기존 고객',
  '내부 직원',
  '파트너',
  '일반 대중',
  '전문가',
  '기타'
];

export function CreateVideoModal({ onClose, onSubmit }: CreateVideoModalProps) {
  const [formData, setFormData] = useState<VideoPlan>({
    title: '',
    description: '',
    status: 'draft',
    category: '',
    duration: '',
    target_audience: ''
  });
  const [customDuration, setCustomDuration] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.title.trim() || !formData.description.trim()) {
      alert('제목과 설명을 모두 입력해주세요.');
      return;
    }

    setIsSubmitting(true);
    try {
      const finalDuration = formData.duration === '사용자 정의' ? customDuration : formData.duration;
      await onSubmit({
        ...formData,
        duration: finalDuration
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleInputChange = (field: keyof VideoPlan, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <Modal
      isOpen={true}
      onClose={onClose}
      title="새 영상 기획 추가"
      size="lg"
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* 제목 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            제목 *
          </label>
          <Input
            type="text"
            value={formData.title}
            onChange={(e) => handleInputChange('title', e.target.value)}
            placeholder="영상 제목을 입력하세요"
            required
          />
        </div>

        {/* 설명 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            설명 *
          </label>
          <textarea
            value={formData.description}
            onChange={(e) => handleInputChange('description', e.target.value)}
            placeholder="영상에 대한 상세 설명을 입력하세요"
            rows={4}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-brand-primary focus:border-brand-primary"
          />
        </div>

        {/* 카테고리와 상태 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              카테고리
            </label>
            <select
              value={formData.category}
              onChange={(e) => handleInputChange('category', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-brand-primary focus:border-brand-primary"
            >
              <option value="">선택해주세요</option>
              {categoryOptions.map((category) => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              상태
            </label>
            <select
              value={formData.status}
              onChange={(e) => handleInputChange('status', e.target.value as VideoPlan['status'])}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-brand-primary focus:border-brand-primary"
            >
              {statusOptions.map((status) => (
                <option key={status.value} value={status.value}>
                  {status.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* 영상 길이 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            영상 길이
          </label>
          <select
            value={formData.duration}
            onChange={(e) => handleInputChange('duration', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-brand-primary focus:border-brand-primary"
          >
            <option value="">선택해주세요</option>
            {durationOptions.map((duration) => (
              <option key={duration} value={duration}>
                {duration}
              </option>
            ))}
          </select>
          
          {formData.duration === '사용자 정의' && (
            <div className="mt-2">
              <Input
                type="text"
                value={customDuration}
                onChange={(e) => setCustomDuration(e.target.value)}
                placeholder="예: 7분 30초"
              />
            </div>
          )}
        </div>

        {/* 타겟 오디언스 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            타겟 오디언스
          </label>
          <select
            value={formData.target_audience}
            onChange={(e) => handleInputChange('target_audience', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-brand-primary focus:border-brand-primary"
          >
            <option value="">선택해주세요</option>
            {audienceOptions.map((audience) => (
              <option key={audience} value={audience}>
                {audience}
              </option>
            ))}
          </select>
        </div>

        {/* 버튼 */}
        <div className="flex gap-3 justify-end pt-4 border-t">
          <Button
            type="button"
            variant="secondary"
            onClick={onClose}
            disabled={isSubmitting}
          >
            취소
          </Button>
          <Button
            type="submit"
            disabled={isSubmitting}
          >
            {isSubmitting ? '생성 중...' : '생성하기'}
          </Button>
        </div>
      </form>
    </Modal>
  );
}