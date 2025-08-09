import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { v4 as uuidv4 } from 'uuid';
import { 
  AIVideoStore, 
  Story, 
  Scene, 
  GenerationProgress, 
  VideoGenerationRequest,
  PromptTemplate 
} from '@/types/ai-video';

const mockPromptTemplates: PromptTemplate[] = [
  {
    id: '1',
    name: '자연 풍경',
    category: 'nature',
    template: 'Beautiful {location} landscape at {time_of_day}, {weather} weather, cinematic lighting',
    variables: ['location', 'time_of_day', 'weather']
  },
  {
    id: '2',
    name: '도시 장면',
    category: 'urban',
    template: 'Modern city {scene_type} with {mood} atmosphere, {lighting} lighting',
    variables: ['scene_type', 'mood', 'lighting']
  },
  {
    id: '3',
    name: '인물 초상',
    category: 'portrait',
    template: 'Professional portrait of {subject}, {expression} expression, {background} background',
    variables: ['subject', 'expression', 'background']
  }
];

export const useAIVideoStore = create<AIVideoStore>()(
  devtools(
    persist(
      (set, get) => ({
        currentStory: null,
        scenes: [],
        generationProgress: {},
        promptTemplates: mockPromptTemplates,
        isGenerating: false,

        setCurrentStory: (story) => 
          set(() => ({ 
            currentStory: story,
            scenes: story.scenes || []
          }), false, 'setCurrentStory'),

        addScene: (sceneData) => {
          const newScene: Scene = {
            ...sceneData,
            id: uuidv4(),
          };
          
          set((state) => ({
            scenes: [...state.scenes, newScene],
            currentStory: state.currentStory ? {
              ...state.currentStory,
              scenes: [...state.scenes, newScene],
              updatedAt: new Date()
            } : null
          }), false, 'addScene');
        },

        updateScene: (id, updates) =>
          set((state) => ({
            scenes: state.scenes.map(scene =>
              scene.id === id ? { ...scene, ...updates } : scene
            ),
            currentStory: state.currentStory ? {
              ...state.currentStory,
              scenes: state.scenes.map(scene =>
                scene.id === id ? { ...scene, ...updates } : scene
              ),
              updatedAt: new Date()
            } : null
          }), false, 'updateScene'),

        removeScene: (id) =>
          set((state) => ({
            scenes: state.scenes.filter(scene => scene.id !== id),
            currentStory: state.currentStory ? {
              ...state.currentStory,
              scenes: state.scenes.filter(scene => scene.id !== id),
              updatedAt: new Date()
            } : null,
            generationProgress: Object.fromEntries(
              Object.entries(state.generationProgress).filter(([key]) => key !== id)
            )
          }), false, 'removeScene'),

        reorderScenes: (fromIndex, toIndex) => {
          const scenes = get().scenes;
          const newScenes = [...scenes];
          const [removed] = newScenes.splice(fromIndex, 1);
          newScenes.splice(toIndex, 0, removed);
          
          // Update positions
          const updatedScenes = newScenes.map((scene, index) => ({
            ...scene,
            position: index
          }));

          set((state) => ({
            scenes: updatedScenes,
            currentStory: state.currentStory ? {
              ...state.currentStory,
              scenes: updatedScenes,
              updatedAt: new Date()
            } : null
          }), false, 'reorderScenes');
        },

        generateVideo: async (request: VideoGenerationRequest) => {
          const { sceneId, prompt, duration } = request;
          
          // Update scene status and add progress tracking
          set((state) => ({
            isGenerating: true,
            generationProgress: {
              ...state.generationProgress,
              [sceneId]: {
                sceneId,
                status: 'processing',
                progress: 0,
                startedAt: new Date(),
                estimatedTime: duration * 2 // Estimate 2 seconds per second of video
              }
            }
          }), false, 'generateVideo:start');

          get().updateScene(sceneId, { status: 'generating' });

          try {
            // Simulate video generation with progress updates
            for (let progress = 10; progress <= 100; progress += 10) {
              await new Promise(resolve => setTimeout(resolve, 500));
              
              set((state) => ({
                generationProgress: {
                  ...state.generationProgress,
                  [sceneId]: {
                    ...state.generationProgress[sceneId],
                    progress
                  }
                }
              }), false, `generateVideo:progress:${progress}`);
            }

            // Simulate successful generation
            const mockVideoUrl = `https://mock-video-url.com/${sceneId}.mp4`;
            const mockThumbnailUrl = `https://mock-thumbnail-url.com/${sceneId}.jpg`;

            get().updateScene(sceneId, {
              status: 'completed',
              videoUrl: mockVideoUrl,
              thumbnailUrl: mockThumbnailUrl,
              generatedAt: new Date()
            });

            set((state) => ({
              generationProgress: {
                ...state.generationProgress,
                [sceneId]: {
                  ...state.generationProgress[sceneId],
                  status: 'completed',
                  progress: 100,
                  completedAt: new Date()
                }
              },
              isGenerating: false
            }), false, 'generateVideo:complete');

          } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Generation failed';
            
            get().updateScene(sceneId, {
              status: 'error',
              errorMessage
            });

            set((state) => ({
              generationProgress: {
                ...state.generationProgress,
                [sceneId]: {
                  ...state.generationProgress[sceneId],
                  status: 'error',
                  errorMessage,
                  completedAt: new Date()
                }
              },
              isGenerating: false
            }), false, 'generateVideo:error');
          }
        },

        updateGenerationProgress: (sceneId, progress) =>
          set((state) => ({
            generationProgress: {
              ...state.generationProgress,
              [sceneId]: {
                ...state.generationProgress[sceneId],
                ...progress
              }
            }
          }), false, 'updateGenerationProgress'),

        loadPromptTemplates: async () => {
          // In a real app, this would fetch from an API
          set(() => ({
            promptTemplates: mockPromptTemplates
          }), false, 'loadPromptTemplates');
        }
      }),
      {
        name: 'ai-video-store',
        partialize: (state) => ({
          currentStory: state.currentStory,
          scenes: state.scenes,
          promptTemplates: state.promptTemplates
        })
      }
    ),
    { name: 'ai-video-store' }
  )
);