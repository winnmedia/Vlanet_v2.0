/**
 *    
 *  API    
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
    basic_plan: ' ',
    story_board: '',
    filming: '',
    video_edit: '',
    post_work: '',
    video_preview: '',
    confirmation: '',
    video_delivery: ''
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      //    
      const validProcess = formData.process.filter(
        p => p.startDate && p.endDate
      );

      if (validProcess.length === 0) {
        throw new Error('     .');
      }

      const projectData = {
        ...formData,
        process: validProcess
      };

      const result = await projectAPI.create(projectData);
      
      if (result.project_id) {
        //      
        router.push(`/projects/${result.project_id}`);
      }
    } catch (error) {
      const handled = errorHandler.handle(error, 'createProject');
      setError(handled.message);
      
      //     
      if (handled.code === 'DUPLICATE_PROJECT_NAME') {
        setError('    .   .');
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
      <h1 className="text-2xl font-bold mb-6">  </h1>
      
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/*   */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4"> </h2>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">
                 *
              </label>
              <input
                type="text"
                required
                value={formData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                className="w-full px-3 py-2 border rounded-md"
                placeholder="  "
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                 *
              </label>
              <input
                type="text"
                required
                value={formData.manager}
                onChange={(e) => handleInputChange('manager', e.target.value)}
                className="w-full px-3 py-2 border rounded-md"
                placeholder=" "
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                 *
              </label>
              <input
                type="text"
                required
                value={formData.consumer}
                onChange={(e) => handleInputChange('consumer', e.target.value)}
                className="w-full px-3 py-2 border rounded-md"
                placeholder=""
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                 
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
               
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
              className="w-full px-3 py-2 border rounded-md"
              rows="3"
              placeholder="   "
            />
          </div>
        </div>

        {/*   */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4"> </h2>
          <p className="text-sm text-gray-600 mb-4">
                . ()
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

        {/*   */}
        <div className="flex justify-end gap-4">
          <button
            type="button"
            onClick={() => router.push('/projects')}
            className="px-6 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
          >
            
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? ' ...' : ' '}
          </button>
        </div>
      </form>
    </div>
  );
}