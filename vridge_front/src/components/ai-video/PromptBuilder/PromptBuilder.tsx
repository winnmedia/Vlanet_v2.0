'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { PromptBuilderProps, PromptTemplate } from '@/types/ai-video';

interface PromptVariable {
  name: string;
  value: string;
  placeholder: string;
}

const STYLE_CATEGORIES = {
  cinematography: {
    name: ' ',
    options: [
      'cinematic lighting',
      'dramatic shadows',
      'soft natural lighting',
      'golden hour',
      'blue hour',
      'high contrast',
      'low key lighting',
      'backlighting'
    ]
  },
  camera: {
    name: ' ',
    options: [
      'close-up shot',
      'medium shot',
      'wide shot',
      'aerial view',
      'bird\'s eye view',
      'low angle',
      'high angle',
      'dutch angle'
    ]
  },
  mood: {
    name: '',
    options: [
      'peaceful',
      'energetic',
      'mysterious',
      'dramatic',
      'romantic',
      'melancholic',
      'cheerful',
      'suspenseful'
    ]
  },
  style: {
    name: ' ',
    options: [
      'realistic',
      'artistic',
      'minimalist',
      'vintage',
      'modern',
      'futuristic',
      'abstract',
      'documentary'
    ]
  }
};

export const PromptBuilder: React.FC<PromptBuilderProps> = ({
  initialPrompt = '',
  templates,
  onPromptChange,
  onGenerate
}) => {
  const [prompt, setPrompt] = useState(initialPrompt);
  const [selectedTemplate, setSelectedTemplate] = useState<PromptTemplate | null>(null);
  const [promptVariables, setPromptVariables] = useState<Record<string, string>>({});
  const [selectedStyles, setSelectedStyles] = useState<Record<string, string>>({});
  const [customPrompt, setCustomPrompt] = useState('');
  const [mode, setMode] = useState<'template' | 'custom'>('template');

  const templateCategories = useMemo(() => {
    const categories: Record<string, PromptTemplate[]> = {};
    templates.forEach(template => {
      if (!categories[template.category]) {
        categories[template.category] = [];
      }
      categories[template.category].push(template);
    });
    return categories;
  }, [templates]);

  const finalPrompt = useMemo(() => {
    let result = '';

    if (mode === 'template' && selectedTemplate) {
      result = selectedTemplate.template;
      
      // Replace template variables
      selectedTemplate.variables.forEach(variable => {
        const value = promptVariables[variable] || '';
        result = result.replace(new RegExp(`{${variable}}`, 'g'), value);
      });
    } else {
      result = customPrompt;
    }

    // Add selected styles
    const styleValues = Object.values(selectedStyles).filter(Boolean);
    if (styleValues.length > 0) {
      result += `, ${styleValues.join(', ')}`;
    }

    return result.trim();
  }, [mode, selectedTemplate, promptVariables, customPrompt, selectedStyles]);

  useEffect(() => {
    if (finalPrompt !== prompt) {
      setPrompt(finalPrompt);
      onPromptChange(finalPrompt);
    }
  }, [finalPrompt]);

  const handleTemplateSelect = (template: PromptTemplate) => {
    setSelectedTemplate(template);
    setPromptVariables({});
    setMode('template');
  };

  const handleVariableChange = (variable: string, value: string) => {
    setPromptVariables(prev => ({
      ...prev,
      [variable]: value
    }));
  };

  const handleStyleToggle = (category: string, style: string) => {
    setSelectedStyles(prev => ({
      ...prev,
      [category]: prev[category] === style ? '' : style
    }));
  };

  const handleCustomModeToggle = () => {
    setMode(mode === 'template' ? 'custom' : 'template');
    if (mode === 'custom') {
      setCustomPrompt('');
    }
  };

  const handleGenerate = () => {
    if (finalPrompt.trim()) {
      onGenerate(finalPrompt);
    }
  };

  const isGenerateDisabled = !finalPrompt.trim() || 
    (mode === 'template' && selectedTemplate && 
     selectedTemplate.variables.some(variable => !promptVariables[variable]?.trim()));

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900"> </h2>
        
        {/* Mode Toggle */}
        <div className="flex items-center bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setMode('template')}
            className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
              mode === 'template'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
             
          </button>
          <button
            onClick={() => setMode('custom')}
            className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
              mode === 'custom'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
             
          </button>
        </div>
      </div>

      <div className="space-y-6">
        {/* Template Mode */}
        {mode === 'template' && (
          <div className="space-y-6">
            {/* Template Categories */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4"> </h3>
              <div className="space-y-4">
                {Object.entries(templateCategories).map(([category, categoryTemplates]) => (
                  <div key={category}>
                    <h4 className="text-sm font-medium text-gray-700 mb-2 capitalize">
                      {category}
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                      {categoryTemplates.map(template => (
                        <button
                          key={template.id}
                          onClick={() => handleTemplateSelect(template)}
                          className={`p-3 text-left border rounded-lg transition-colors ${
                            selectedTemplate?.id === template.id
                              ? 'border-blue-500 bg-blue-50 text-blue-900'
                              : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                          }`}
                        >
                          <div className="font-medium text-sm">{template.name}</div>
                          <div className="text-xs text-gray-500 mt-1 line-clamp-2">
                            {template.template.replace(/\{([^}]+)\}/g, '[]')}
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Template Variables */}
            {selectedTemplate && selectedTemplate.variables.length > 0 && (
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4"> </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {selectedTemplate.variables.map(variable => (
                    <div key={variable}>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        {variable.replace('_', ' ')}
                        <span className="text-red-500 ml-1">*</span>
                      </label>
                      <input
                        type="text"
                        value={promptVariables[variable] || ''}
                        onChange={(e) => handleVariableChange(variable, e.target.value)}
                        placeholder={`${variable}() `}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Custom Mode */}
        {mode === 'custom' && (
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4"> </h3>
            <textarea
              value={customPrompt}
              onChange={(e) => setCustomPrompt(e.target.value)}
              placeholder="    ..."
              rows={4}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-vertical"
            />
          </div>
        )}

        {/* Style Options */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4"> </h3>
          <div className="space-y-4">
            {Object.entries(STYLE_CATEGORIES).map(([categoryKey, category]) => (
              <div key={categoryKey}>
                <h4 className="text-sm font-medium text-gray-700 mb-2">{category.name}</h4>
                <div className="flex flex-wrap gap-2">
                  {category.options.map(option => (
                    <button
                      key={option}
                      onClick={() => handleStyleToggle(categoryKey, option)}
                      className={`px-3 py-1 text-sm rounded-full border transition-colors ${
                        selectedStyles[categoryKey] === option
                          ? 'border-blue-500 bg-blue-100 text-blue-800'
                          : 'border-gray-300 text-gray-700 hover:border-gray-400 hover:bg-gray-50'
                      }`}
                    >
                      {option}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Preview */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4"> </h3>
          <div className="bg-gray-50 rounded-lg p-4">
            <pre className="text-sm text-gray-800 whitespace-pre-wrap font-mono">
              {finalPrompt || ' ...'}
            </pre>
          </div>
        </div>

        {/* Character Count */}
        <div className="flex items-center justify-between text-sm text-gray-500">
          <span>{finalPrompt.length} </span>
          <div className="flex items-center space-x-4">
            <span className={finalPrompt.length > 500 ? 'text-orange-500' : ''}>
              : 500 
            </span>
            {finalPrompt.length > 1000 && (
              <span className="text-red-500">       </span>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end space-x-3 pt-6 border-t">
          <button
            onClick={() => {
              setPrompt('');
              setSelectedTemplate(null);
              setPromptVariables({});
              setSelectedStyles({});
              setCustomPrompt('');
              onPromptChange('');
            }}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-lg hover:bg-gray-200 transition-colors"
          >
            
          </button>

          <button
            onClick={() => {
              navigator.clipboard.writeText(finalPrompt);
              // TODO: Add toast notification
            }}
            disabled={!finalPrompt.trim()}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            
          </button>

          <button
            onClick={handleGenerate}
            disabled={isGenerateDisabled}
            className="px-6 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
             
          </button>
        </div>

        {/* Help Text */}
        {isGenerateDisabled && selectedTemplate && (
          <p className="text-sm text-orange-600 bg-orange-50 rounded-lg p-3">
                   .
          </p>
        )}
      </div>
    </div>
  );
};