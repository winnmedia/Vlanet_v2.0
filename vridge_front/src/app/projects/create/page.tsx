'use client';

import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { ArrowLeft, Plus, Lightbulb, Rocket, Users, Target } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { CreateProjectModal } from '@/components/projects';
import { useProjectStore } from '@/store/project.store';
import { Toaster } from 'sonner';

// QueryClient 
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,
      gcTime: 1000 * 60 * 30,
      retry: 2,
    },
  },
});

// ========================================
//   
// ========================================

const projectTemplates = [
  {
    id: 'brand-video',
    title: '  ',
    description: '       ',
    icon: Target,
    color: 'bg-blue-50 border-blue-200 text-blue-600',
    estimatedDuration: '2-4',
    complexity: '',
    tags: ['', '', ''],
  },
  {
    id: 'tutorial-video',
    title: '/ ',
    description: '       ',
    icon: Lightbulb,
    color: 'bg-green-50 border-green-200 text-green-600',
    estimatedDuration: '1-2',
    complexity: '',
    tags: ['', '', ''],
  },
  {
    id: 'event-video',
    title: '/ ',
    description: ', ,       ',
    icon: Users,
    color: 'bg-purple-50 border-purple-200 text-purple-600',
    estimatedDuration: '3-5',
    complexity: '',
    tags: ['', '', ''],
  },
  {
    id: 'product-video',
    title: '  ',
    description: '        ',
    icon: Rocket,
    color: 'bg-orange-50 border-orange-200 text-orange-600',
    estimatedDuration: '2-3',
    complexity: '',
    tags: ['', '', ''],
  },
];

// ========================================
//  
// ========================================

interface ProjectTemplateCardProps {
  template: typeof projectTemplates[0];
  onSelect: (templateId: string) => void;
}

const ProjectTemplateCard: React.FC<ProjectTemplateCardProps> = ({
  template,
  onSelect,
}) => {
  const Icon = template.icon;

  return (
    <motion.div
      whileHover={{ y: -4 }}
      whileTap={{ scale: 0.98 }}
      className="bg-white rounded-xl border border-gray-200 p-6 cursor-pointer hover:border-gray-300 hover:shadow-lg transition-all duration-200"
      onClick={() => onSelect(template.id)}
    >
      <div className="flex items-start gap-4">
        <div className={`p-3 rounded-lg ${template.color}`}>
          <Icon className="w-6 h-6" />
        </div>
        
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            {template.title}
          </h3>
          <p className="text-gray-600 text-sm mb-4 leading-relaxed">
            {template.description}
          </p>
          
          <div className="flex items-center gap-4 text-xs text-gray-500 mb-3">
            <div className="flex items-center gap-1">
              <span> :</span>
              <span className="font-medium">{template.estimatedDuration}</span>
            </div>
            <div className="flex items-center gap-1">
              <span>:</span>
              <span className="font-medium">{template.complexity}</span>
            </div>
          </div>
          
          <div className="flex flex-wrap gap-1">
            {template.tags.map(tag => (
              <span
                key={tag}
                className="inline-flex items-center px-2 py-1 bg-gray-100 text-gray-700 rounded-md text-xs"
              >
                {tag}
              </span>
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  );
};

interface CreateProjectHeaderProps {
  onBack: () => void;
}

const CreateProjectHeader: React.FC<CreateProjectHeaderProps> = ({ onBack }) => {
  return (
    <div className="bg-white border-b border-gray-200">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/*    */}
        <div className="mb-8">
          <Button
            variant="ghost"
            onClick={onBack}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="w-4 h-4" />
             
          </Button>
        </div>

        {/*   */}
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-6">
            <Plus className="w-8 h-8 text-blue-600" />
          </div>
          
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
              
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
               .       .
          </p>
        </div>
      </div>
    </div>
  );
};

interface CreateProjectContentProps {
  onCreateFromTemplate: (templateId: string) => void;
  onCreateBlank: () => void;
}

const CreateProjectContent: React.FC<CreateProjectContentProps> = ({
  onCreateFromTemplate,
  onCreateBlank,
}) => {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/*    */}
      <div className="mb-12">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
             
          </h2>
          <p className="text-gray-600">
                 ,    .
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {/*    */}
          <motion.div
            whileHover={{ y: -2 }}
            whileTap={{ scale: 0.98 }}
            className="bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-dashed border-blue-300 rounded-xl p-8 text-center cursor-pointer hover:border-blue-400 transition-colors"
            onClick={onCreateBlank}
          >
            <div className="inline-flex items-center justify-center w-12 h-12 bg-blue-100 rounded-lg mb-4">
              <Plus className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
                
            </h3>
            <p className="text-gray-600 text-sm">
                  
            </p>
          </motion.div>

          {/* AI   ( ) */}
          <motion.div
            whileHover={{ y: -2 }}
            className="bg-gradient-to-br from-purple-50 to-pink-50 border-2 border-dashed border-purple-300 rounded-xl p-8 text-center opacity-75 cursor-not-allowed"
          >
            <div className="inline-flex items-center justify-center w-12 h-12 bg-purple-100 rounded-lg mb-4">
              <Lightbulb className="w-6 h-6 text-purple-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              AI  
              <span className="ml-2 px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded-full">
                
              </span>
            </h3>
            <p className="text-gray-600 text-sm">
              AI    
            </p>
          </motion.div>
        </div>
      </div>

      {/*   */}
      <div>
        <div className="text-center mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
             
          </h2>
          <p className="text-gray-600">
                   .
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {projectTemplates.map((template) => (
            <ProjectTemplateCard
              key={template.id}
              template={template}
              onSelect={onCreateFromTemplate}
            />
          ))}
        </div>
      </div>

      {/*   */}
      <div className="mt-16 bg-gray-50 rounded-xl p-8">
        <div className="text-center">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
              ?
          </h3>
          <p className="text-gray-600 mb-6">
            VideoPlanet      .
          </p>
          <div className="flex items-center justify-center gap-4">
            <Button variant="outline" size="sm">
                
            </Button>
            <Button variant="ghost" size="sm">
                
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

// ========================================
//     
// ========================================

const CreateProjectPageContent: React.FC = () => {
  const router = useRouter();
  const { openCreateModal, createModalOpen, closeAllModals } = useProjectStore();
  const [_selectedTemplate, _setSelectedTemplate] = React.useState<string | null>(null);

  //  
  const handleBack = () => {
    router.push('/projects');
  };

  //   
  const handleCreateBlank = () => {
    _setSelectedTemplate(null);
    openCreateModal();
  };

  //   
  const handleCreateFromTemplate = (templateId: string) => {
    _setSelectedTemplate(templateId);
    openCreateModal();
  };

  //   
  const handleCreateSuccess = (projectId: number) => {
    router.push(`/projects/${projectId}`);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="min-h-screen bg-gray-50"
    >
      {/*  */}
      <CreateProjectHeader onBack={handleBack} />

      {/*  */}
      <CreateProjectContent
        onCreateFromTemplate={handleCreateFromTemplate}
        onCreateBlank={handleCreateBlank}
      />

      {/*    */}
      <CreateProjectModal
        isOpen={createModalOpen}
        onClose={closeAllModals}
        onSuccess={handleCreateSuccess}
      />

      {/*   */}
      <Toaster position="top-right" />
    </motion.div>
  );
};

// ========================================
//   
// ========================================

export default function CreateProjectPage() {
  return (
    <QueryClientProvider client={queryClient}>
      <CreateProjectPageContent />
    </QueryClientProvider>
  );
}