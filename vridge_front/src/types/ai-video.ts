export interface Scene {
  id: string;
  title: string;
  description: string;
  prompt: string;
  duration: number;
  position: number;
  status: 'draft' | 'generating' | 'completed' | 'error';
  videoUrl?: string;
  thumbnailUrl?: string;
  generatedAt?: Date;
  errorMessage?: string;
}

export interface Story {
  id: string;
  title: string;
  description: string;
  totalDuration: number;
  scenes: Scene[];
  createdAt: Date;
  updatedAt: Date;
  status: 'draft' | 'processing' | 'completed' | 'error';
}

export interface PromptTemplate {
  id: string;
  name: string;
  category: string;
  template: string;
  variables: string[];
}

export interface GenerationProgress {
  sceneId: string;
  status: 'queued' | 'processing' | 'completed' | 'error';
  progress: number;
  estimatedTime?: number;
  startedAt?: Date;
  completedAt?: Date;
  errorMessage?: string;
}

export interface VideoGenerationRequest {
  sceneId: string;
  prompt: string;
  duration: number;
  style?: string;
  quality?: 'low' | 'medium' | 'high';
}

export interface AIVideoStore {
  currentStory: Story | null;
  scenes: Scene[];
  generationProgress: Record<string, GenerationProgress>;
  promptTemplates: PromptTemplate[];
  isGenerating: boolean;
  
  // Actions
  setCurrentStory: (story: Story) => void;
  addScene: (scene: Omit<Scene, 'id'>) => void;
  updateScene: (id: string, updates: Partial<Scene>) => void;
  removeScene: (id: string) => void;
  reorderScenes: (fromIndex: number, toIndex: number) => void;
  generateVideo: (request: VideoGenerationRequest) => Promise<void>;
  updateGenerationProgress: (sceneId: string, progress: Partial<GenerationProgress>) => void;
  loadPromptTemplates: () => Promise<void>;
}

export interface StoryEditorProps {
  story?: Story;
  onSave: (story: Partial<Story>) => void;
  onCancel?: () => void;
}

export interface SceneTimelineProps {
  scenes: Scene[];
  onSceneSelect: (scene: Scene) => void;
  onSceneReorder: (fromIndex: number, toIndex: number) => void;
  onSceneUpdate: (id: string, updates: Partial<Scene>) => void;
}

export interface PromptBuilderProps {
  initialPrompt?: string;
  templates: PromptTemplate[];
  onPromptChange: (prompt: string) => void;
  onGenerate: (prompt: string) => void;
}

export interface GenerationProgressProps {
  progress: Record<string, GenerationProgress>;
  onCancel?: (sceneId: string) => void;
}

export interface VideoPreviewProps {
  scenes: Scene[];
  currentScene?: Scene;
  onSceneChange: (scene: Scene) => void;
  autoPlay?: boolean;
}