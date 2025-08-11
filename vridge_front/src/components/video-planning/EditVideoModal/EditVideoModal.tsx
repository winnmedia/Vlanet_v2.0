'use client';

import React, { useState, useEffect } from 'react';
import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

interface VideoPlan {
  id: string;
  title: string;
  description: string;
  status: 'draft' | 'in_progress' | 'completed';
  created_at: string;
  updated_at: string;
  category: string;
  duration: string;
  target_audience: string;
}

interface EditVideoModalProps {
  video: VideoPlan;
  onClose: () => void;
  onSubmit: (video: VideoPlan) => void;
}

const categoryOptions = [
  '',
  '',
  '',
  '',
  '',
  '',
  ''
];

const statusOptions = [
  { value: 'draft', label: '' },
  { value: 'in_progress', label: ' ' },
  { value: 'completed', label: '' }
];

const durationOptions = [
  '30',
  '1',
  '2',
  '3',
  '5',
  '10',
  '15',
  '30',
  ' '
];

const audienceOptions = [
  ' ',
  ' ',
  ' ',
  '',
  ' ',
  '',
  ''
];

export function EditVideoModal({ video, onClose, onSubmit }: EditVideoModalProps) {
  const [formData, setFormData] = useState<VideoPlan>(video);
  const [customDuration, setCustomDuration] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  //   duration 
  useEffect(() => {
    if (video.duration && !durationOptions.slice(0, -1).includes(video.duration)) {
      setCustomDuration(video.duration);
      setFormData(prev => ({
        ...prev,
        duration: ' '
      }));
    }
  }, [video]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.title.trim() || !formData.description.trim()) {
      alert('   .');
      return;
    }

    setIsSubmitting(true);
    try {
      const finalDuration = formData.duration === ' ' ? customDuration : formData.duration;
      await onSubmit({
        ...formData,
        duration: finalDuration,
        updated_at: new Date().toISOString()
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
      title="  "
      size="lg"
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        {/*  */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
             *
          </label>
          <Input
            type="text"
            value={formData.title}
            onChange={(e) => handleInputChange('title', e.target.value)}
            placeholder="  "
            required
          />
        </div>

        {/*  */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
             *
          </label>
          <textarea
            value={formData.description}
            onChange={(e) => handleInputChange('description', e.target.value)}
            placeholder="    "
            rows={4}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-brand-primary focus:border-brand-primary"
          />
        </div>

        {/*   */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              
            </label>
            <select
              value={formData.category}
              onChange={(e) => handleInputChange('category', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-brand-primary focus:border-brand-primary"
            >
              <option value=""></option>
              {categoryOptions.map((category) => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              
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

        {/*   */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
             
          </label>
          <select
            value={formData.duration}
            onChange={(e) => handleInputChange('duration', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-brand-primary focus:border-brand-primary"
          >
            <option value=""></option>
            {durationOptions.map((duration) => (
              <option key={duration} value={duration}>
                {duration}
              </option>
            ))}
          </select>
          
          {formData.duration === ' ' && (
            <div className="mt-2">
              <Input
                type="text"
                value={customDuration}
                onChange={(e) => setCustomDuration(e.target.value)}
                placeholder=": 7 30"
              />
            </div>
          )}
        </div>

        {/*   */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
             
          </label>
          <select
            value={formData.target_audience}
            onChange={(e) => handleInputChange('target_audience', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-brand-primary focus:border-brand-primary"
          >
            <option value=""></option>
            {audienceOptions.map((audience) => (
              <option key={audience} value={audience}>
                {audience}
              </option>
            ))}
          </select>
        </div>

        {/* /   */}
        <div className="text-sm text-gray-500 bg-gray-50 p-3 rounded-md">
          <div>: {new Date(formData.created_at).toLocaleString('ko-KR')}</div>
          <div>: {new Date(formData.updated_at).toLocaleString('ko-KR')}</div>
        </div>

        {/*  */}
        <div className="flex gap-3 justify-end pt-4 border-t">
          <Button
            type="button"
            variant="secondary"
            onClick={onClose}
            disabled={isSubmitting}
          >
            
          </Button>
          <Button
            type="submit"
            disabled={isSubmitting}
          >
            {isSubmitting ? ' ...' : ''}
          </Button>
        </div>
      </form>
    </Modal>
  );
}