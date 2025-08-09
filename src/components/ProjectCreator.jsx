/**
 * 프로젝트 생성 컴포넌트 예시
 * 백엔드 API와 통합된 실제 사용 예시
 */

import React, { useState } from 'react';
import { projectAPI, errorHandler } from '@/services/api-integration';
import { useRouter } from 'next/navigation';

export default function ProjectCreator() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    manager: '',
    consumer: '',
    description: '',
    color: '#1631F8',
    process: [
      { key: 'basic_plan', startDate: '', endDate: '' },
      { key: 'story_board', startDate: '', endDate: '' },
      { key: 'filming', startDate: '', endDate: '' },
      { key: 'video_edit', startDate: '', endDate: '' },
      { key: 'post_work', startDate: '', endDate: '' },
      { key: 'video_preview', startDate: '', endDate: '' },
      { key: 'confirmation', startDate: '', endDate: '' },
      { key: 'video_delivery', startDate: '', endDate: '' }
    ]
  });

  const processNames = {
    basic_plan: '기초 기획안',
    story_board: '스토리보드',
    filming: '촬영',
    video_edit: '편집',
    post_work: '후반작업',
    video_preview: '시사',
    confirmation: '최종컨펌',
    video_delivery: '납품'
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // 날짜가 입력된 프로세스만 필터링
      const validProcess = formData.process.filter(
        p => p.startDate && p.endDate
      );

      if (validProcess.length === 0) {
        throw new Error('최소 하나 이상의 작업 일정을 입력해주세요.');
      }

      const projectData = {
        ...formData,
        process: validProcess
      };

      const result = await projectAPI.create(projectData);
      
      if (result.project_id) {
        // 성공 시 프로젝트 상세 페이지로 이동
        router.push(`/projects/${result.project_id}`);
      }
    } catch (error) {
      const handled = errorHandler.handle(error, 'createProject');
      setError(handled.message);
      
      // 특정 에러 코드에 따른 처리
      if (handled.code === 'DUPLICATE_PROJECT_NAME') {
        setError('이미 같은 이름의 프로젝트가 존재합니다. 다른 이름을 사용해주세요.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleProcessChange = (index, field, value) => {
    setFormData(prev => ({
      ...prev,
      process: prev.process.map((p, i) => 
        i === index ? { ...p, [field]: value } : p
      )
    }));
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">새 프로젝트 만들기</h1>
      
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* 기본 정보 */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">기본 정보</h2>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">
                프로젝트명 *
              </label>
              <input
                type="text"
                required
                value={formData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                className="w-full px-3 py-2 border rounded-md"
                placeholder="프로젝트 이름을 입력하세요"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                담당자 *
              </label>
              <input
                type="text"
                required
                value={formData.manager}
                onChange={(e) => handleInputChange('manager', e.target.value)}
                className="w-full px-3 py-2 border rounded-md"
                placeholder="담당자 이름"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                고객사 *
              </label>
              <input
                type="text"
                required
                value={formData.consumer}
                onChange={(e) => handleInputChange('consumer', e.target.value)}
                className="w-full px-3 py-2 border rounded-md"
                placeholder="고객사명"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                프로젝트 색상
              </label>
              <input
                type="color"
                value={formData.color}
                onChange={(e) => handleInputChange('color', e.target.value)}
                className="w-full h-10"
              />
            </div>
          </div>

          <div className="mt-4">
            <label className="block text-sm font-medium mb-1">
              프로젝트 설명
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
              className="w-full px-3 py-2 border rounded-md"
              rows="3"
              placeholder="프로젝트에 대한 설명을 입력하세요"
            />
          </div>
        </div>

        {/* 작업 일정 */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">작업 일정</h2>
          <p className="text-sm text-gray-600 mb-4">
            각 단계별 시작일과 종료일을 설정하세요. (선택사항)
          </p>

          <div className="space-y-3">
            {formData.process.map((process, index) => (
              <div key={process.key} className="flex items-center gap-4">
                <div className="w-32 text-sm font-medium">
                  {processNames[process.key]}
                </div>
                <input
                  type="date"
                  value={process.startDate}
                  onChange={(e) => handleProcessChange(index, 'startDate', e.target.value)}
                  className="px-3 py-1 border rounded"
                />
                <span>~</span>
                <input
                  type="date"
                  value={process.endDate}
                  onChange={(e) => handleProcessChange(index, 'endDate', e.target.value)}
                  min={process.startDate}
                  className="px-3 py-1 border rounded"
                />
              </div>
            ))}
          </div>
        </div>

        {/* 제출 버튼 */}
        <div className="flex justify-end gap-4">
          <button
            type="button"
            onClick={() => router.push('/projects')}
            className="px-6 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
          >
            취소
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? '생성 중...' : '프로젝트 생성'}
          </button>
        </div>
      </form>
    </div>
  );
}