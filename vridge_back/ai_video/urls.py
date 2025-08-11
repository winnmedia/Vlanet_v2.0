"""
URL configuration for AI Video Generation API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StoryViewSet,
    SceneViewSet,
    ScenePromptViewSet,
    JobViewSet,
    StoryDevelopmentViewSet
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'stories', StoryViewSet, basename='story')
router.register(r'scenes', SceneViewSet, basename='scene')
router.register(r'prompts', ScenePromptViewSet, basename='prompt')
router.register(r'jobs', JobViewSet, basename='job')
router.register(r'story-development', StoryDevelopmentViewSet, basename='story-development')

app_name = 'ai_video'

urlpatterns = [
    path('', include(router.urls)),
]

# API Endpoints Summary:
# 
# Stories:
# - GET    /api/ai-video/stories/                         - List all stories
# - POST   /api/ai-video/stories/                         - Create new story
# - GET    /api/ai-video/stories/{id}/                    - Get story details
# - PUT    /api/ai-video/stories/{id}/                    - Update story
# - DELETE /api/ai-video/stories/{id}/                    - Delete story
# - POST   /api/ai-video/stories/{id}/transition/         - Transition story status
# - POST   /api/ai-video/stories/{id}/lock/               - Lock story ( )
# - POST   /api/ai-video/stories/{id}/unlock/             - Unlock story ( )
# - POST   /api/ai-video/stories/{id}/scenes/bulk/        - Create 12 scenes in bulk
# - POST   /api/ai-video/stories/{id}/generate-prompts/   - Generate AI prompts
# - POST   /api/ai-video/stories/{id}/generate_preview/   - Generate preview
# - POST   /api/ai-video/stories/{id}/render_final/       - Render final video
# - GET    /api/ai-video/stories/{id}/transitions/        - Get transition history
# - GET    /api/ai-video/stories/{id}/jobs/               - Get story jobs
# - GET    /api/ai-video/stories/{id}/cost_estimate/      - Get cost estimate
# - GET    /api/ai-video/stories/statistics/              - Get user statistics
#
# Scenes:
# - GET    /api/ai-video/scenes/                     - List all scenes
# - POST   /api/ai-video/scenes/                     - Create new scene
# - POST   /api/ai-video/scenes/bulk_create/         - Bulk create scenes
# - GET    /api/ai-video/scenes/{id}/                - Get scene details
# - PUT    /api/ai-video/scenes/{id}/                - Update scene
# - DELETE /api/ai-video/scenes/{id}/                - Delete scene
# - POST   /api/ai-video/scenes/{id}/generate/       - Generate scene content
# - POST   /api/ai-video/scenes/{id}/reorder/        - Reorder scene
#
# Prompts:
# - GET    /api/ai-video/prompts/                    - List all prompts
# - POST   /api/ai-video/prompts/                    - Create new prompt
# - GET    /api/ai-video/prompts/{id}/               - Get prompt details
# - PUT    /api/ai-video/prompts/{id}/               - Update prompt
# - DELETE /api/ai-video/prompts/{id}/               - Delete prompt
# - POST   /api/ai-video/prompts/{id}/select/        - Select prompt as active
# - POST   /api/ai-video/prompts/{id}/test/          - Test prompt generation
#
# Jobs:
# - GET    /api/ai-video/jobs/                       - List all jobs
# - GET    /api/ai-video/jobs/{id}/                  - Get job details
# - POST   /api/ai-video/jobs/{id}/retry/            - Retry failed job
# - POST   /api/ai-video/jobs/{id}/cancel/           - Cancel job
# - GET    /api/ai-video/jobs/statistics/            - Get job statistics
#
# Story Development (NEW):
# - POST   /api/ai-video/story-development/analyze-project/        - Analyze project settings
# - POST   /api/ai-video/story-development/generate-story-outline/  - Generate story outline
# - GET    /api/ai-video/story-development/genre-templates/         - Get genre templates
# - GET    /api/ai-video/story-development/style-guide/             - Get style guide
#
# Enhanced Story Actions (NEW):
# - POST   /api/ai-video/stories/{id}/develop-story/               - Develop story from project
# - POST   /api/ai-video/stories/{id}/generate-storyboard/         - Generate storyboard ()
# - POST   /api/ai-video/stories/{id}/generate-pdf-brief/          - Generate PDF brief
#
# Enhanced Scene Actions (NEW):
# - POST   /api/ai-video/scenes/{id}/generate-storyboard-image/    - Generate storyboard image