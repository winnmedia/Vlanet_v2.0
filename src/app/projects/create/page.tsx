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

// QueryClient 인스턴스
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
// 프로젝트 템플릿 데이터
// ========================================

const projectTemplates = [
  {
    id: 'brand-video',
    title: '브랜드 홍보 영상',
    description: '기업이나 제품의 브랜드 가치를 전달하는 홍보 영상 프로젝트',
    icon: Target,
    color: 'bg-blue-50 border-blue-200 text-blue-600',
    estimatedDuration: '2-4주',
    complexity: '중간',
    tags: ['브랜딩', '마케팅', '홍보'],
  },
  {
    id: 'tutorial-video',
    title: '교육/튜토리얼 영상',
    description: '제품 사용법이나 교육 콘텐츠를 위한 튜토리얼 영상 프로젝트',
    icon: Lightbulb,
    color: 'bg-green-50 border-green-200 text-green-600',
    estimatedDuration: '1-2주',
    complexity: '쉬움',
    tags: ['교육', '가이드', '설명'],
  },
  {
    id: 'event-video',
    title: '이벤트/행사 영상',
    description: '컨퍼런스, 세미나, 행사 등의 기록 및 홍보 영상 프로젝트',
    icon: Users,
    color: 'bg-purple-50 border-purple-200 text-purple-600',
    estimatedDuration: '3-5주',
    complexity: '복잡',
    tags: ['이벤트', '행사', '기록'],
  },
  {
    id: 'product-video',
    title: '제품 소개 영상',
    description: '신제품 출시나 기능 소개를 위한 제품 중심의 영상 프로젝트',
    icon: Rocket,
    color: 'bg-orange-50 border-orange-200 text-orange-600',
    estimatedDuration: '2-3주',
    complexity: '중간',
    tags: ['제품', '소개', '출시'],
  },
];

// ========================================
// 하위 컴포넌트들
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
              <span>예상 기간:</span>
              <span className="font-medium">{template.estimatedDuration}</span>
            </div>
            <div className="flex items-center gap-1">
              <span>복잡도:</span>
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
        {/* 뒤로 가기 버튼 */}
        <div className="mb-8">
          <Button
            variant="ghost"
            onClick={onBack}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="w-4 h-4" />
            프로젝트 목록으로
          </Button>
        </div>

        {/* 헤더 내용 */}
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-6">
            <Plus className="w-8 h-8 text-blue-600" />
          </div>
          
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            새 프로젝트 만들기
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            영상 제작 프로젝트를 시작해보세요. 템플릿을 선택하거나 처음부터 새로 만들 수 있습니다.
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
      {/* 빠른 시작 섹션 */}
      <div className="mb-12">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
            빠른 시작
          </h2>
          <p className="text-gray-600">
            자주 사용되는 템플릿으로 빠르게 프로젝트를 시작하거나, 완전히 새로운 프로젝트를 만드세요.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {/* 빈 프로젝트 생성 */}
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
              빈 프로젝트 만들기
            </h3>
            <p className="text-gray-600 text-sm">
              처음부터 완전히 새로운 프로젝트를 시작합니다
            </p>
          </motion.div>

          {/* AI 도움으로 생성 (미래 기능) */}
          <motion.div
            whileHover={{ y: -2 }}
            className="bg-gradient-to-br from-purple-50 to-pink-50 border-2 border-dashed border-purple-300 rounded-xl p-8 text-center opacity-75 cursor-not-allowed"
          >
            <div className="inline-flex items-center justify-center w-12 h-12 bg-purple-100 rounded-lg mb-4">
              <Lightbulb className="w-6 h-6 text-purple-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              AI로 프로젝트 생성
              <span className="ml-2 px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded-full">
                준비중
              </span>
            </h3>
            <p className="text-gray-600 text-sm">
              AI가 제안하는 맞춤형 프로젝트를 생성합니다
            </p>
          </motion.div>
        </div>
      </div>

      {/* 템플릿 섹션 */}
      <div>
        <div className="text-center mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
            프로젝트 템플릿
          </h2>
          <p className="text-gray-600">
            업계에서 검증된 템플릿으로 더 빠르고 효율적으로 프로젝트를 시작하세요.
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

      {/* 도움말 섹션 */}
      <div className="mt-16 bg-gray-50 rounded-xl p-8">
        <div className="text-center">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            프로젝트 생성이 처음이신가요?
          </h3>
          <p className="text-gray-600 mb-6">
            VideoPlanet의 프로젝트 관리 기능에 대한 가이드를 확인해보세요.
          </p>
          <div className="flex items-center justify-center gap-4">
            <Button variant="outline" size="sm">
              사용 가이드 보기
            </Button>
            <Button variant="ghost" size="sm">
              샘플 프로젝트 둘러보기
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

// ========================================
// 메인 프로젝트 생성 페이지 컴포넌트
// ========================================

const CreateProjectPageContent: React.FC = () => {
  const router = useRouter();
  const { openCreateModal, createModalOpen, closeAllModals } = useProjectStore();
  const [_selectedTemplate, _setSelectedTemplate] = React.useState<string | null>(null);

  // 뒤로 가기
  const handleBack = () => {
    router.push('/projects');
  };

  // 빈 프로젝트 생성
  const handleCreateBlank = () => {
    _setSelectedTemplate(null);
    openCreateModal();
  };

  // 템플릿으로 프로젝트 생성
  const handleCreateFromTemplate = (templateId: string) => {
    _setSelectedTemplate(templateId);
    openCreateModal();
  };

  // 프로젝트 생성 성공
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
      {/* 헤더 */}
      <CreateProjectHeader onBack={handleBack} />

      {/* 내용 */}
      <CreateProjectContent
        onCreateFromTemplate={handleCreateFromTemplate}
        onCreateBlank={handleCreateBlank}
      />

      {/* 프로젝트 생성 모달 */}
      <CreateProjectModal
        isOpen={createModalOpen}
        onClose={closeAllModals}
        onSuccess={handleCreateSuccess}
      />

      {/* 토스트 알림 */}
      <Toaster position="top-right" />
    </motion.div>
  );
};

// ========================================
// 메인 페이지 컴포넌트
// ========================================

export default function CreateProjectPage() {
  return (
    <QueryClientProvider client={queryClient}>
      <CreateProjectPageContent />
    </QueryClientProvider>
  );
}