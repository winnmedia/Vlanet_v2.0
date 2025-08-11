'use client';

import { useState } from 'react';
import { 
  Download, 
  FileText, 
  Table, 
  Image, 
  Calendar,
  Filter,
  CheckCircle2,
  Clock,
  FileSpreadsheet,
  FileImage,
  Play
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import { videoFeedbackService } from '@/lib/api/video-feedback.service';
import type { 
  VideoFile, 
  TimelineFeedback, 
  VideoFeedbackStats,
  FeedbackCategory,
  FeedbackPriority,
  FeedbackStatus
} from '@/types/video-feedback';
import { useToast } from '@/contexts/toast.context';

interface FeedbackExporterProps {
  video: VideoFile;
  feedbacks: TimelineFeedback[];
  stats?: VideoFeedbackStats;
  isOpen: boolean;
  onClose: () => void;
}

interface ExportOptions {
  format: 'pdf' | 'excel' | 'json' | 'timeline';
  includeResolved: boolean;
  includeDeclined: boolean;
  categories: FeedbackCategory[];
  priorities: FeedbackPriority[];
  dateRange?: {
    start: string;
    end: string;
  };
  includeReplies: boolean;
  includeTimestamps: boolean;
  includeScreenshots: boolean;
  groupBy: 'timestamp' | 'category' | 'priority' | 'author';
  sortBy: 'timestamp' | 'created_at' | 'priority';
  sortOrder: 'asc' | 'desc';
}

const EXPORT_FORMATS = [
  {
    id: 'pdf',
    label: 'PDF ',
    description: '   PDF  ',
    icon: <FileText size={20} />,
    color: 'text-red-600'
  },
  {
    id: 'excel',
    label: 'Excel ',
    description: '  Excel  ',
    icon: <FileSpreadsheet size={20} />,
    color: 'text-green-600'
  },
  {
    id: 'timeline',
    label: ' HTML',
    description: '   ',
    icon: <Play size={20} />,
    color: 'text-purple-600'
  },
  {
    id: 'json',
    label: 'JSON ',
    description: '   ',
    icon: <Table size={20} />,
    color: 'text-blue-600'
  }
];

const CATEGORIES: FeedbackCategory[] = [
  'general', 'correction', 'question', 'approval', 'suggestion', 'technical', 'creative'
];

const PRIORITIES: FeedbackPriority[] = ['low', 'medium', 'high', 'urgent'];

export default function FeedbackExporter({
  video,
  feedbacks,
  stats,
  isOpen,
  onClose
}: FeedbackExporterProps) {
  const { success, error } = useToast();
  
  const [options, setOptions] = useState<ExportOptions>({
    format: 'pdf',
    includeResolved: true,
    includeDeclined: false,
    categories: [...CATEGORIES],
    priorities: [...PRIORITIES],
    includeReplies: true,
    includeTimestamps: true,
    includeScreenshots: false,
    groupBy: 'timestamp',
    sortBy: 'timestamp',
    sortOrder: 'asc'
  });
  
  const [isExporting, setIsExporting] = useState(false);
  const [exportProgress, setExportProgress] = useState(0);

  //   
  const filteredFeedbacks = feedbacks.filter(feedback => {
    if (!options.includeResolved && feedback.status === 'resolved') return false;
    if (!options.includeDeclined && feedback.status === 'declined') return false;
    if (!options.categories.includes(feedback.category)) return false;
    if (!options.priorities.includes(feedback.priority)) return false;
    
    if (options.dateRange) {
      const feedbackDate = new Date(feedback.created_at);
      const startDate = new Date(options.dateRange.start);
      const endDate = new Date(options.dateRange.end);
      if (feedbackDate < startDate || feedbackDate > endDate) return false;
    }
    
    return true;
  });

  //  
  const handleExport = async () => {
    if (filteredFeedbacks.length === 0) {
      error('  .   .');
      return;
    }

    setIsExporting(true);
    setExportProgress(0);

    try {
      //  
      const progressInterval = setInterval(() => {
        setExportProgress(prev => Math.min(prev + 10, 90));
      }, 200);

      let result;
      
      switch (options.format) {
        case 'pdf':
        case 'excel':
          result = await videoFeedbackService.exportFeedbackReport(video.id, options.format);
          break;
        case 'timeline':
          result = await videoFeedbackService.exportTimeline(video.id);
          break;
        case 'json':
          // JSON   
          const jsonData = {
            video: {
              id: video.id,
              title: video.title,
              duration: video.duration
            },
            export_info: {
              exported_at: new Date().toISOString(),
              total_feedbacks: filteredFeedbacks.length,
              filters: options
            },
            feedbacks: filteredFeedbacks.map(feedback => ({
              ...feedback,
              replies: options.includeReplies ? feedback.replies : undefined
            })),
            stats: stats
          };
          
          const blob = new Blob([JSON.stringify(jsonData, null, 2)], { 
            type: 'application/json' 
          });
          const url = URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          link.download = `${video.title}_feedback_${new Date().toISOString().split('T')[0]}.json`;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          URL.revokeObjectURL(url);
          
          clearInterval(progressInterval);
          setExportProgress(100);
          success('JSON  .');
          onClose();
          return;
      }

      clearInterval(progressInterval);
      setExportProgress(100);

      if (result?.success && result.data?.download_url) {
        //  
        window.open(result.data.download_url, '_blank');
        success('  .');
        onClose();
      } else {
        throw new Error(' .');
      }
    } catch (err) {
      console.error(' :', err);
      error(' .');
    } finally {
      setIsExporting(false);
      setExportProgress(0);
    }
  };

  //  
  const getPreviewData = () => {
    const totalFeedbacks = filteredFeedbacks.length;
    const resolvedCount = filteredFeedbacks.filter(f => f.status === 'resolved').length;
    const categoryCounts = CATEGORIES.reduce((acc, category) => {
      acc[category] = filteredFeedbacks.filter(f => f.category === category).length;
      return acc;
    }, {} as Record<FeedbackCategory, number>);

    return {
      totalFeedbacks,
      resolvedCount,
      resolutionRate: totalFeedbacks > 0 ? (resolvedCount / totalFeedbacks * 100).toFixed(1) : '0',
      categoryCounts
    };
  };

  const previewData = getPreviewData();

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title=" "
      className="max-w-4xl"
    >
      <div className="space-y-6">
        {/*    */}
        <div>
          <h4 className="text-lg font-medium text-gray-800 mb-4"> </h4>
          <div className="grid grid-cols-2 gap-4">
            {EXPORT_FORMATS.map((format) => (
              <button
                key={format.id}
                onClick={() => setOptions(prev => ({ ...prev, format: format.id as any }))}
                className={`p-4 border-2 rounded-lg text-left transition-colors ${
                  options.format === format.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center gap-3 mb-2">
                  <div className={format.color}>
                    {format.icon}
                  </div>
                  <h5 className="font-medium text-gray-800">{format.label}</h5>
                </div>
                <p className="text-sm text-gray-600">{format.description}</p>
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/*   */}
          <div>
            <h4 className="text-lg font-medium text-gray-800 mb-4"> </h4>
            <div className="space-y-4">
              {/*   */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">  </label>
                <div className="space-y-2">
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={options.includeResolved}
                      onChange={(e) => setOptions(prev => ({ ...prev, includeResolved: e.target.checked }))}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <CheckCircle2 size={16} className="text-green-500" />
                    <span className="text-sm"> </span>
                  </label>
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={options.includeDeclined}
                      onChange={(e) => setOptions(prev => ({ ...prev, includeDeclined: e.target.checked }))}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm"> </span>
                  </label>
                </div>
              </div>

              {/*   */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2"></label>
                <div className="grid grid-cols-2 gap-2 max-h-32 overflow-y-auto">
                  {CATEGORIES.map((category) => (
                    <label key={category} className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={options.categories.includes(category)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setOptions(prev => ({ 
                              ...prev, 
                              categories: [...prev.categories, category] 
                            }));
                          } else {
                            setOptions(prev => ({ 
                              ...prev, 
                              categories: prev.categories.filter(c => c !== category) 
                            }));
                          }
                        }}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="text-sm capitalize">{category}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/*   */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">  ()</label>
                <div className="grid grid-cols-2 gap-2">
                  <input
                    type="date"
                    value={options.dateRange?.start || ''}
                    onChange={(e) => setOptions(prev => ({
                      ...prev,
                      dateRange: {
                        start: e.target.value,
                        end: prev.dateRange?.end || ''
                      }
                    }))}
                    className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                  <input
                    type="date"
                    value={options.dateRange?.end || ''}
                    onChange={(e) => setOptions(prev => ({
                      ...prev,
                      dateRange: {
                        start: prev.dateRange?.start || '',
                        end: e.target.value
                      }
                    }))}
                    className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
            </div>
          </div>

          {/*     */}
          <div>
            <h4 className="text-lg font-medium text-gray-800 mb-4"> </h4>
            <div className="space-y-4">
              {/*   */}
              <div className="space-y-2">
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={options.includeReplies}
                    onChange={(e) => setOptions(prev => ({ ...prev, includeReplies: e.target.checked }))}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm"> </span>
                </label>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={options.includeTimestamps}
                    onChange={(e) => setOptions(prev => ({ ...prev, includeTimestamps: e.target.checked }))}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <Clock size={16} className="text-blue-500" />
                  <span className="text-sm"> </span>
                </label>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={options.includeScreenshots}
                    onChange={(e) => setOptions(prev => ({ ...prev, includeScreenshots: e.target.checked }))}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <Image size={16} className="text-green-500" />
                  <span className="text-sm"> </span>
                </label>
              </div>

              {/*   */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1"> </label>
                  <select
                    value={options.sortBy}
                    onChange={(e) => setOptions(prev => ({ ...prev, sortBy: e.target.value as any }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="timestamp"> </option>
                    <option value="created_at"></option>
                    <option value="priority"></option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1"> </label>
                  <select
                    value={options.sortOrder}
                    onChange={(e) => setOptions(prev => ({ ...prev, sortOrder: e.target.value as any }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="asc"></option>
                    <option value="desc"></option>
                  </select>
                </div>
              </div>

              {/*  */}
              <div className="bg-blue-50 p-4 rounded-lg">
                <h5 className="font-medium text-blue-800 mb-3"> </h5>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-blue-700"> :</span>
                    <span className="font-medium text-blue-800">{previewData.totalFeedbacks}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-blue-700">:</span>
                    <span className="font-medium text-blue-800">{previewData.resolutionRate}%</span>
                  </div>
                  {previewData.totalFeedbacks > 0 && (
                    <div className="pt-2 border-t border-blue-200">
                      <div className="text-blue-700 mb-1">:</div>
                      {Object.entries(previewData.categoryCounts)
                        .filter(([, count]) => count > 0)
                        .map(([category, count]) => (
                          <div key={category} className="flex justify-between text-xs">
                            <span className="capitalize">{category}:</span>
                            <span>{count}</span>
                          </div>
                        ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/*  */}
        {isExporting && (
          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700"> ...</span>
              <span className="text-sm text-gray-600">{exportProgress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${exportProgress}%` }}
              />
            </div>
          </div>
        )}

        {/*   */}
        <div className="flex gap-3 pt-4 border-t">
          <Button
            onClick={handleExport}
            disabled={isExporting || filteredFeedbacks.length === 0}
            className="flex-1 bg-blue-600 hover:bg-blue-700 text-white flex items-center justify-center gap-2"
          >
            {isExporting ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
            ) : (
              <Download size={16} />
            )}
            {isExporting ? ' ...' : `${previewData.totalFeedbacks}  `}
          </Button>
          
          <Button
            variant="ghost"
            onClick={onClose}
            disabled={isExporting}
            className="px-6"
          >
            
          </Button>
        </div>
      </div>
    </Modal>
  );
}