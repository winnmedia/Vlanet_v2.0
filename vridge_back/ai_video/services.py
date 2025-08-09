"""
Service layer for AI Video Generation
Implements business logic, external integrations, and queue management
"""
import json
import uuid
import logging
from decimal import Decimal
from typing import Dict, Any, Optional, List
from django.conf import settings
from django.utils import timezone
from django.db import transaction
import requests

# Redis를 선택적으로 임포트
try:
    import redis
    HAS_REDIS = True
except ImportError:
    redis = None
    HAS_REDIS = False

from .models import (
    Story, Scene, ScenePrompt, Job,
    StoryStatus, JobStatus, AIProvider,
    AIProviderConfig
)
from projects.models import Project

logger = logging.getLogger(__name__)


class StoryDevelopmentService:
    """
    Advanced story development service
    Implements AI-powered story evolution based on user settings
    """
    
    # 장르별 스토리 발전 템플릿
    GENRE_TEMPLATES = {
        'action': {
            'opening': 'High-energy opening with dynamic movement',
            'development': 'Escalating tension with fast-paced sequences',
            'climax': 'Intense action sequence with dramatic effects',
            'resolution': 'Powerful conclusion with satisfying resolution'
        },
        'drama': {
            'opening': 'Emotional setup establishing character connections',
            'development': 'Building emotional tension through character interactions',
            'climax': 'Emotional peak moment with deep character revelation',
            'resolution': 'Thoughtful resolution with character growth'
        },
        'comedy': {
            'opening': 'Light, humorous introduction with comedic timing',
            'development': 'Escalating comedic situations with visual gags',
            'climax': 'Peak comedic moment with unexpected twist',
            'resolution': 'Satisfying comedic payoff'
        },
        'horror': {
            'opening': 'Ominous atmosphere building with subtle tension',
            'development': 'Escalating dread with unsettling imagery',
            'climax': 'Terrifying peak moment with maximum impact',
            'resolution': 'Haunting conclusion leaving lasting impression'
        },
        'documentary': {
            'opening': 'Informative introduction establishing the topic',
            'development': 'Evidence presentation with compelling visuals',
            'climax': 'Key revelation or turning point in narrative',
            'resolution': 'Conclusive summary with call to action'
        },
        'commercial': {
            'opening': 'Attention-grabbing hook showcasing product benefit',
            'development': 'Problem-solution narrative with product demonstration',
            'climax': 'Product showcase with emotional appeal',
            'resolution': 'Strong call-to-action with brand reinforcement'
        }
    }
    
    # 톤별 시각적 스타일
    TONE_STYLES = {
        'professional': {
            'visual_style': 'clean, minimalist, corporate aesthetic',
            'lighting': 'bright, even lighting',
            'composition': 'structured, balanced framing',
            'color_palette': 'neutral tones with brand colors'
        },
        'casual': {
            'visual_style': 'natural, approachable, lifestyle',
            'lighting': 'natural, soft lighting',
            'composition': 'relaxed, candid framing',
            'color_palette': 'warm, friendly colors'
        },
        'dramatic': {
            'visual_style': 'cinematic, high-contrast, artistic',
            'lighting': 'dramatic shadows and highlights',
            'composition': 'dynamic angles and depth',
            'color_palette': 'bold, contrasting colors'
        },
        'playful': {
            'visual_style': 'vibrant, energetic, fun',
            'lighting': 'bright, colorful lighting',
            'composition': 'dynamic, varied angles',
            'color_palette': 'bright, saturated colors'
        },
        'elegant': {
            'visual_style': 'sophisticated, refined, luxurious',
            'lighting': 'soft, flattering lighting',
            'composition': 'graceful, well-balanced framing',
            'color_palette': 'muted, sophisticated tones'
        },
        'edgy': {
            'visual_style': 'bold, unconventional, cutting-edge',
            'lighting': 'high contrast, dramatic lighting',
            'composition': 'unusual angles, creative framing',
            'color_palette': 'bold, unexpected color combinations'
        }
    }
    
    # 강도별 비주얼 인텐시티
    INTENSITY_LEVELS = {
        1: {'motion': 'minimal', 'effects': 'subtle', 'pace': 'slow'},
        2: {'motion': 'gentle', 'effects': 'soft', 'pace': 'relaxed'},
        3: {'motion': 'moderate', 'effects': 'balanced', 'pace': 'medium'},
        4: {'motion': 'active', 'effects': 'noticeable', 'pace': 'energetic'},
        5: {'motion': 'dynamic', 'effects': 'strong', 'pace': 'fast'},
        6: {'motion': 'intense', 'effects': 'dramatic', 'pace': 'rapid'},
        7: {'motion': 'powerful', 'effects': 'bold', 'pace': 'very fast'},
        8: {'motion': 'explosive', 'effects': 'striking', 'pace': 'extreme'},
        9: {'motion': 'extreme', 'effects': 'overwhelming', 'pace': 'frantic'},
        10: {'motion': 'maximum', 'effects': 'spectacular', 'pace': 'breakneck'}
    }
    
    @staticmethod
    def develop_story_from_project(project: Project) -> Dict[str, Any]:
        """
        프로젝트 설정에 기반하여 스토리를 발전시킵니다
        """
        try:
            # 프로젝트 메타데이터에서 설정값 추출
            project_data = project.project_data or {}
            
            genre = project_data.get('genre', 'commercial')
            tone = project_data.get('tone', 'professional')
            intensity = project_data.get('intensity', 5)
            target_audience = project_data.get('target_audience', 'general')
            key_message = project_data.get('key_message', '')
            brand_values = project_data.get('brand_values', [])
            
            # 스토리 구조 생성
            story_structure = StoryDevelopmentService._create_story_structure(
                genre, tone, intensity, target_audience, key_message, brand_values
            )
            
            # 씬별 프롬프트 생성
            scene_prompts = StoryDevelopmentService._generate_scene_prompts(
                story_structure, genre, tone, intensity
            )
            
            # 인서트 샷 추천
            insert_shots = StoryDevelopmentService._suggest_insert_shots(
                genre, tone, brand_values
            )
            
            return {
                'success': True,
                'story_structure': story_structure,
                'scene_prompts': scene_prompts,
                'insert_shots': insert_shots,
                'style_guide': {
                    'genre': genre,
                    'tone': tone,
                    'intensity': intensity,
                    'visual_style': StoryDevelopmentService.TONE_STYLES.get(tone, {}),
                    'intensity_guide': StoryDevelopmentService.INTENSITY_LEVELS.get(intensity, {})
                }
            }
        
        except Exception as e:
            logger.error(f"Error developing story: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def _create_story_structure(genre: str, tone: str, intensity: int, 
                              target_audience: str, key_message: str, brand_values: List[str]) -> Dict:
        """장르와 톤에 맞는 스토리 구조 생성"""
        
        template = StoryDevelopmentService.GENRE_TEMPLATES.get(genre, 
                   StoryDevelopmentService.GENRE_TEMPLATES['commercial'])
        
        tone_style = StoryDevelopmentService.TONE_STYLES.get(tone, 
                     StoryDevelopmentService.TONE_STYLES['professional'])
        
        intensity_guide = StoryDevelopmentService.INTENSITY_LEVELS.get(intensity, 
                         StoryDevelopmentService.INTENSITY_LEVELS[5])
        
        # 타겟 오디언스별 어조 조정
        audience_adjustments = {
            'teenagers': 'energetic and trendy language with modern references',
            'young_adults': 'authentic and relatable with aspirational elements',
            'professionals': 'polished and credible with industry expertise',
            'families': 'warm and inclusive with universal appeal',
            'seniors': 'respectful and clear with trusted messaging'
        }
        
        audience_tone = audience_adjustments.get(target_audience, 
                       'appropriate and engaging for the target demographic')
        
        return {
            'act1_opening': f"{template['opening']} with {tone_style['visual_style']}, "
                           f"incorporating {intensity_guide['motion']} motion and {audience_tone}",
            'act2_development': f"{template['development']} featuring {tone_style['composition']} "
                               f"with {intensity_guide['effects']} effects at {intensity_guide['pace']} pace",
            'act3_climax': f"{template['climax']} utilizing {tone_style['lighting']} "
                          f"and {tone_style['color_palette']} to maximize emotional impact",
            'act4_resolution': f"{template['resolution']} that reinforces {key_message} "
                              f"and aligns with brand values: {', '.join(brand_values)}",
            'overall_theme': f"A {genre} story with {tone} tone at intensity level {intensity}, "
                            f"designed for {target_audience} audience"
        }
    
    @staticmethod
    def _generate_scene_prompts(story_structure: Dict, genre: str, tone: str, intensity: int) -> List[Dict]:
        """스토리 구조를 바탕으로 씬별 프롬프트 생성"""
        
        tone_style = StoryDevelopmentService.TONE_STYLES.get(tone, 
                     StoryDevelopmentService.TONE_STYLES['professional'])
        intensity_guide = StoryDevelopmentService.INTENSITY_LEVELS.get(intensity, 
                         StoryDevelopmentService.INTENSITY_LEVELS[5])
        
        # 12개 씬을 4개 액트에 배분 (3-3-3-3)
        scenes = [
            # Act 1: Opening (Scenes 1-3)
            {
                'scene_number': 1,
                'act': 'opening',
                'title': 'Hook Scene',
                'description': f"Opening hook that {story_structure['act1_opening']}",
                'visual_prompt': f"Cinematic establishing shot, {tone_style['visual_style']}, "
                               f"{tone_style['lighting']}, {intensity_guide['motion']} camera movement",
                'duration': 2.5,
                'scene_type': 'intro'
            },
            {
                'scene_number': 2,
                'act': 'opening',
                'title': 'Context Setup',
                'description': f"Context establishment with {tone_style['composition']}",
                'visual_prompt': f"Medium shot showcasing environment, {tone_style['color_palette']}, "
                               f"{intensity_guide['effects']} visual effects",
                'duration': 2.5,
                'scene_type': 'main'
            },
            {
                'scene_number': 3,
                'act': 'opening',
                'title': 'Character Introduction',
                'description': f"Character/product introduction with appropriate tone",
                'visual_prompt': f"Close-up or product shot, {tone_style['lighting']}, "
                               f"emphasizing key features with {intensity_guide['pace']} pacing",
                'duration': 2.5,
                'scene_type': 'main'
            },
            
            # Act 2: Development (Scenes 4-6)
            {
                'scene_number': 4,
                'act': 'development',
                'title': 'Rising Action',
                'description': f"Development that {story_structure['act2_development']}",
                'visual_prompt': f"Dynamic sequence with {intensity_guide['motion']} movement, "
                               f"{tone_style['visual_style']}, building tension",
                'duration': 2.5,
                'scene_type': 'main'
            },
            {
                'scene_number': 5,
                'act': 'development',
                'title': 'Conflict/Challenge',
                'description': f"Challenge presentation with {intensity_guide['effects']} impact",
                'visual_prompt': f"Dramatic angle, {tone_style['composition']}, heightened {tone_style['lighting']}",
                'duration': 2.5,
                'scene_type': 'main'
            },
            {
                'scene_number': 6,
                'act': 'development',
                'title': 'Transition',
                'description': f"Transitional moment building toward climax",
                'visual_prompt': f"Transition shot with {intensity_guide['motion']} camera work, "
                               f"maintaining {tone_style['color_palette']}",
                'duration': 2.5,
                'scene_type': 'transition'
            },
            
            # Act 3: Climax (Scenes 7-9)
            {
                'scene_number': 7,
                'act': 'climax',
                'title': 'Peak Moment',
                'description': f"Climactic moment that {story_structure['act3_climax']}",
                'visual_prompt': f"High-impact shot with maximum {intensity_guide['effects']}, "
                               f"{tone_style['lighting']}, {intensity_guide['pace']} editing",
                'duration': 2.5,
                'scene_type': 'main'
            },
            {
                'scene_number': 8,
                'act': 'climax',
                'title': 'Resolution Setup',
                'description': f"Setting up resolution with emotional peak",
                'visual_prompt': f"Emotional close-up or reveal shot, {tone_style['visual_style']}, "
                               f"dramatic {tone_style['lighting']}",
                'duration': 2.5,
                'scene_type': 'main'
            },
            {
                'scene_number': 9,
                'act': 'climax',
                'title': 'Emotional Peak',
                'description': f"Maximum emotional impact moment",
                'visual_prompt': f"Powerful visual with {intensity_guide['motion']} dynamics, "
                               f"utilizing full {tone_style['color_palette']}",
                'duration': 2.5,
                'scene_type': 'main'
            },
            
            # Act 4: Resolution (Scenes 10-12)
            {
                'scene_number': 10,
                'act': 'resolution',
                'title': 'Resolution',
                'description': f"Resolution that {story_structure['act4_resolution']}",
                'visual_prompt': f"Satisfying resolution shot, {tone_style['composition']}, "
                               f"balanced {tone_style['lighting']}",
                'duration': 2.5,
                'scene_type': 'main'
            },
            {
                'scene_number': 11,
                'act': 'resolution',
                'title': 'Brand Integration',
                'description': f"Brand message integration with natural flow",
                'visual_prompt': f"Product/brand showcase, {tone_style['visual_style']}, "
                               f"professional {tone_style['lighting']}",
                'duration': 2.5,
                'scene_type': 'main'
            },
            {
                'scene_number': 12,
                'act': 'resolution',
                'title': 'Call to Action',
                'description': f"Strong closing with clear call to action",
                'visual_prompt': f"Final impact shot, {tone_style['color_palette']}, "
                               f"memorable closing with {intensity_guide['effects']}",
                'duration': 2.5,
                'scene_type': 'outro'
            }
        ]
        
        return scenes
    
    @staticmethod
    def _suggest_insert_shots(genre: str, tone: str, brand_values: List[str]) -> List[Dict]:
        """장르와 톤에 맞는 인서트 샷 추천"""
        
        base_inserts = {
            'action': [
                {'type': 'detail', 'description': 'Quick detail shots of key actions'},
                {'type': 'reaction', 'description': 'Intense reaction close-ups'},
                {'type': 'environment', 'description': 'Dynamic environment shots'}
            ],
            'drama': [
                {'type': 'emotion', 'description': 'Subtle emotional detail shots'},
                {'type': 'metaphor', 'description': 'Symbolic imagery for emotional depth'},
                {'type': 'texture', 'description': 'Tactile close-ups for intimacy'}
            ],
            'commercial': [
                {'type': 'product', 'description': 'Elegant product detail shots'},
                {'type': 'lifestyle', 'description': 'Lifestyle integration moments'},
                {'type': 'benefit', 'description': 'Visual benefit demonstrations'}
            ]
        }
        
        tone_adjustments = {
            'professional': 'clean and polished execution',
            'casual': 'natural and authentic feeling',
            'dramatic': 'high contrast and artistic',
            'playful': 'vibrant and energetic',
            'elegant': 'sophisticated and refined',
            'edgy': 'bold and unconventional'
        }
        
        genre_inserts = base_inserts.get(genre, base_inserts['commercial'])
        tone_style = tone_adjustments.get(tone, 'appropriate for target audience')
        
        enhanced_inserts = []
        for insert in genre_inserts:
            enhanced_inserts.append({
                **insert,
                'style_note': f"{insert['description']} with {tone_style}",
                'brand_integration': f"Subtly incorporate {', '.join(brand_values[:2])} values" if brand_values else "Maintain brand consistency"
            })
        
        return enhanced_inserts


class AIVideoService:
    """
    Main service for AI video generation operations
    Handles AI provider integration and video processing logic
    """
    
    @staticmethod
    def calculate_cost_estimate(story: Story) -> Dict[str, Decimal]:
        """Calculate estimated cost for story generation"""
        try:
            # Get provider configuration
            provider_config = AIProviderConfig.objects.get(
                provider=story.ai_provider,
                is_active=True
            )
            
            # Calculate scene generation costs
            scene_count = story.scenes.count()
            scene_cost = scene_count * provider_config.cost_per_image
            
            # Calculate video generation costs
            video_cost = story.duration_seconds * provider_config.cost_per_second_video
            
            # Calculate preview cost (lower quality = 50% of final)
            preview_cost = video_cost * Decimal('0.5')
            
            # Storage cost estimate (rough estimate)
            storage_cost = Decimal('0.10')  # $0.10 per video
            
            total_cost = scene_cost + preview_cost + video_cost + storage_cost
            
            return {
                'scene_generation': scene_cost,
                'preview': preview_cost,
                'final_render': video_cost,
                'storage': storage_cost,
                'total': total_cost
            }
        
        except AIProviderConfig.DoesNotExist:
            logger.error(f"No active provider config for {story.ai_provider}")
            return {
                'scene_generation': Decimal('0'),
                'preview': Decimal('0'),
                'final_render': Decimal('0'),
                'storage': Decimal('0'),
                'total': Decimal('0')
            }
        except Exception as e:
            logger.error(f"Error calculating cost estimate: {str(e)}")
            return {
                'scene_generation': Decimal('0'),
                'preview': Decimal('0'),
                'final_render': Decimal('0'),
                'storage': Decimal('0'),
                'total': Decimal('0')
            }
    
    @staticmethod
    def estimate_render_time(story: Story) -> int:
        """Estimate rendering time in seconds"""
        base_time = 60  # Base processing time
        scene_time = story.scenes.count() * 30  # 30 seconds per scene
        duration_time = story.duration_seconds * 2  # 2x real-time for processing
        
        # Add complexity factors
        if story.resolution == '3840x2160':  # 4K
            duration_time *= 2
        elif story.resolution == '1920x1080':  # Full HD
            duration_time *= 1.5
        
        if story.fps == 60:
            duration_time *= 1.5
        
        return base_time + scene_time + int(duration_time)
    
    @staticmethod
    def test_prompt(prompt: ScenePrompt) -> Dict[str, Any]:
        """Test a prompt without saving results"""
        try:
            # Get provider configuration
            provider_config = AIProviderConfig.objects.get(
                provider=prompt.scene.story.ai_provider,
                is_active=True
            )
            
            # Prepare test parameters
            test_params = {
                **prompt.parameters,
                'test_mode': True,
                'low_quality': True  # Use lower quality for testing
            }
            
            # Call appropriate provider
            if prompt.prompt_type == 'image':
                result = AIProviderIntegration.generate_image(
                    provider_config,
                    prompt.user_prompt,
                    test_params
                )
            elif prompt.prompt_type == 'video':
                result = AIProviderIntegration.generate_video(
                    provider_config,
                    prompt.user_prompt,
                    test_params
                )
            else:
                result = {'success': False, 'error': 'Unsupported prompt type'}
            
            return result
        
        except Exception as e:
            logger.error(f"Error testing prompt {prompt.id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def process_story_planning(story: Story) -> bool:
        """Process story planning phase"""
        try:
            with transaction.atomic():
                # Update story status
                story.status = StoryStatus.PLANNING
                story.planning_started_at = timezone.now()
                story.save()
                
                # Auto-generate scenes if not exists
                if not story.scenes.exists():
                    AIVideoService._auto_generate_scenes(story)
                
                # Generate prompts for each scene
                for scene in story.scenes.all():
                    if not scene.prompts.exists():
                        AIVideoService._generate_scene_prompts(scene)
                
                # Calculate cost estimate
                estimate = AIVideoService.calculate_cost_estimate(story)
                story.estimated_cost = estimate['total']
                
                # Transition to planned
                story.status = StoryStatus.PLANNED
                story.planning_completed_at = timezone.now()
                story.save()
                
                return True
        
        except Exception as e:
            logger.error(f"Error processing story planning: {str(e)}")
            story.status = StoryStatus.FAILED
            story.save()
            return False
    
    @staticmethod
    def _auto_generate_scenes(story: Story):
        """Auto-generate scenes based on story duration"""
        # Calculate scene duration (5-10 seconds per scene)
        scene_duration = 7  # Default 7 seconds per scene
        num_scenes = max(1, story.duration_seconds // scene_duration)
        
        scenes = []
        for i in range(num_scenes):
            start_time = i * scene_duration
            end_time = min((i + 1) * scene_duration, story.duration_seconds)
            
            scene_type = 'intro' if i == 0 else 'outro' if i == num_scenes - 1 else 'main'
            
            scene = Scene(
                story=story,
                order=i + 1,
                title=f"Scene {i + 1}",
                description=f"Auto-generated scene {i + 1}",
                start_time=start_time,
                end_time=end_time,
                duration=end_time - start_time,
                scene_type=scene_type
            )
            scenes.append(scene)
        
        Scene.objects.bulk_create(scenes)
    
    @staticmethod
    def _generate_scene_prompts(scene: Scene):
        """Generate default prompts for a scene"""
        # Get project settings if available
        project_data = {}
        if hasattr(scene.story, 'project') and scene.story.project:
            project_data = scene.story.project.project_data or {}
        
        genre = project_data.get('genre', 'commercial')
        tone = project_data.get('tone', 'professional')
        intensity = project_data.get('intensity', 5)
        
        # Get enhanced prompts using story development service
        enhanced_prompt = StoryDevelopmentService._create_enhanced_prompt(
            scene, genre, tone, intensity
        )
        
        # Create image generation prompt
        image_prompt = ScenePrompt.objects.create(
            scene=scene,
            prompt_type='image',
            user_prompt=enhanced_prompt['image_prompt'],
            parameters={
                'width': 1920,
                'height': 1080,
                'steps': 30,
                'cfg_scale': 7.5,
                **enhanced_prompt.get('image_parameters', {})
            },
            is_selected=True
        )
        
        # Create video generation prompt if needed
        if scene.duration > 0:
            video_prompt = ScenePrompt.objects.create(
                scene=scene,
                prompt_type='video',
                user_prompt=enhanced_prompt['video_prompt'],
                parameters={
                    'width': 1920,
                    'height': 1080,
                    'fps': scene.story.fps,
                    'duration': scene.duration,
                    'motion_bucket_id': enhanced_prompt.get('motion_intensity', 127),
                    **enhanced_prompt.get('video_parameters', {})
                }
            )
    
    @staticmethod
    def _create_enhanced_prompt(scene: Scene, genre: str, tone: str, intensity: int) -> Dict:
        """장르, 톤, 강도를 반영한 향상된 프롬프트 생성"""
        tone_style = StoryDevelopmentService.TONE_STYLES.get(tone, 
                     StoryDevelopmentService.TONE_STYLES['professional'])
        intensity_guide = StoryDevelopmentService.INTENSITY_LEVELS.get(intensity, 
                         StoryDevelopmentService.INTENSITY_LEVELS[5])
        
        # 기본 프롬프트 생성
        base_prompt = f"A cinematic shot for {scene.title}. {scene.description}"
        
        # 톤과 스타일을 반영한 시각적 요소
        visual_elements = f", {tone_style['visual_style']}, {tone_style['lighting']}, {tone_style['composition']}"
        
        # 강도에 따른 모션과 효과
        motion_effects = f", {intensity_guide['motion']} motion, {intensity_guide['effects']} effects"
        
        # 장르별 특화 요소
        genre_elements = {
            'action': ', dynamic action, high energy',
            'drama': ', emotional depth, character focus',
            'comedy': ', light-hearted, visually appealing',
            'horror': ', ominous atmosphere, dramatic shadows',
            'documentary': ', authentic, informative visual',
            'commercial': ', professional, brand-focused'
        }
        
        genre_addon = genre_elements.get(genre, ', professional quality')
        
        # 최종 프롬프트 조합
        enhanced_image_prompt = base_prompt + visual_elements + genre_addon + ', high quality, professional cinematography'
        enhanced_video_prompt = base_prompt + visual_elements + motion_effects + genre_addon + ', smooth camera movement'
        
        # Motion intensity 매핑 (1-10을 BullMQ motion_bucket_id로 변환)
        motion_mapping = {
            1: 40, 2: 60, 3: 80, 4: 100, 5: 127,  # 기본값 127
            6: 150, 7: 175, 8: 200, 9: 220, 10: 255
        }
        
        return {
            'image_prompt': enhanced_image_prompt,
            'video_prompt': enhanced_video_prompt,
            'motion_intensity': motion_mapping.get(intensity, 127),
            'image_parameters': {
                'style_preset': f'{genre}_{tone}',
                'clip_guidance_preset': 'FAST_BLUE' if intensity > 7 else 'SIMPLE'
            },
            'video_parameters': {
                'motion_bucket_id': motion_mapping.get(intensity, 127),
                'conditioning_augmentation': min(0.02 + (intensity * 0.01), 0.15)
            }
        }


class QueueService:
    """
    Service for managing job queue operations
    Interfaces with BullMQ/Redis for async processing
    """
    
    def __init__(self):
        if HAS_REDIS:
            try:
                self.redis_client = redis.Redis(
                    host=getattr(settings, 'REDIS_HOST', 'localhost'),
                    port=getattr(settings, 'REDIS_PORT', 6379),
                    db=getattr(settings, 'REDIS_DB', 0),
                    decode_responses=True
                )
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}")
                self.redis_client = None
        else:
            self.redis_client = None
    
    @classmethod
    def create_planning_job(cls, story: Story) -> Job:
        """Create a job for story planning"""
        job_id = f"planning_{story.id}_{uuid.uuid4().hex[:8]}"
        
        job = Job.objects.create(
            job_id=job_id,
            queue_name='ai-video-planning',
            story=story,
            job_type='story_planning',
            status=JobStatus.QUEUED,
            payload={
                'story_id': str(story.id),
                'action': 'plan_story'
            },
            priority=5
        )
        
        # Queue job in Redis
        cls._queue_job(job)
        
        return job
    
    @classmethod
    def create_preview_job(cls, story: Story, **kwargs) -> Job:
        """Create a job for preview generation"""
        job_id = f"preview_{story.id}_{uuid.uuid4().hex[:8]}"
        
        job = Job.objects.create(
            job_id=job_id,
            queue_name='ai-video-generation',
            story=story,
            job_type='preview_generation',
            status=JobStatus.QUEUED,
            payload={
                'story_id': str(story.id),
                'action': 'generate_preview',
                **kwargs
            },
            priority=3
        )
        
        cls._queue_job(job)
        
        return job
    
    @classmethod
    def create_render_job(cls, story: Story, **kwargs) -> Job:
        """Create a job for final video rendering"""
        job_id = f"render_{story.id}_{uuid.uuid4().hex[:8]}"
        
        job = Job.objects.create(
            job_id=job_id,
            queue_name='ai-video-generation',
            story=story,
            job_type='final_render',
            status=JobStatus.QUEUED,
            payload={
                'story_id': str(story.id),
                'action': 'render_final',
                **kwargs
            },
            priority=1  # Lower priority for final renders
        )
        
        cls._queue_job(job)
        
        return job
    
    @classmethod
    def create_scene_generation_job(cls, scene: Scene, prompt: ScenePrompt) -> Job:
        """Create a job for scene content generation"""
        job_id = f"scene_{scene.id}_{uuid.uuid4().hex[:8]}"
        
        job = Job.objects.create(
            job_id=job_id,
            queue_name='ai-video-generation',
            scene=scene,
            story=scene.story,
            job_type='scene_generation',
            status=JobStatus.QUEUED,
            payload={
                'scene_id': str(scene.id),
                'prompt_id': str(prompt.id),
                'action': 'generate_scene'
            },
            priority=4
        )
        
        cls._queue_job(job)
        
        return job
    
    @classmethod
    def retry_job(cls, job: Job, delay: int = 0) -> bool:
        """Retry a failed job"""
        try:
            job.status = JobStatus.QUEUED
            job.save()
            
            # Re-queue with delay if specified
            if delay > 0:
                job.scheduled_at = timezone.now() + timezone.timedelta(seconds=delay)
                job.save()
            
            cls._queue_job(job)
            
            return True
        
        except Exception as e:
            logger.error(f"Error retrying job {job.id}: {str(e)}")
            return False
    
    @classmethod
    def cancel_job(cls, job: Job) -> bool:
        """Cancel a pending or running job"""
        try:
            # Send cancellation signal to Redis if available
            service = cls()
            if service.redis_client:
                service.redis_client.publish(
                    f"job:cancel:{job.queue_name}",
                    json.dumps({
                        'job_id': job.job_id,
                        'timestamp': timezone.now().isoformat()
                    })
                )
            
            return True
        
        except Exception as e:
            logger.error(f"Error cancelling job {job.id}: {str(e)}")
            return False
    
    @classmethod
    def _queue_job(cls, job: Job):
        """Internal method to queue job in Redis"""
        try:
            service = cls()
            
            # Skip Redis if not available (development mode)
            if not service.redis_client:
                logger.info(f"Redis not available, job {job.job_id} stored in DB only")
                return
            
            # Prepare job data for queue
            job_data = {
                'id': job.job_id,
                'name': job.job_type,
                'data': job.payload,
                'opts': {
                    'priority': job.priority,
                    'attempts': job.max_attempts,
                    'backoff': {
                        'type': 'exponential',
                        'delay': 2000
                    }
                }
            }
            
            # Add to queue
            if job.scheduled_at and job.scheduled_at > timezone.now():
                # Scheduled job
                delay = (job.scheduled_at - timezone.now()).total_seconds() * 1000
                job_data['opts']['delay'] = int(delay)
            
            # Push to Redis queue (simplified version)
            service.redis_client.lpush(
                f"bull:{job.queue_name}:wait",
                json.dumps(job_data)
            )
            
            # Update job counter
            service.redis_client.incr(f"bull:{job.queue_name}:id")
            
            logger.info(f"Queued job {job.job_id} to {job.queue_name}")
        
        except Exception as e:
            logger.error(f"Error queuing job {job.id}: {str(e)}")
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            job.save()


class StorageService:
    """
    Service for managing file storage operations
    Interfaces with MinIO/S3 for media storage
    """
    
    @staticmethod
    def upload_video(file_path: str, key: str) -> str:
        """Upload video file to storage and return URL"""
        try:
            # TODO: Implement MinIO/S3 upload
            # For now, return a placeholder URL
            base_url = settings.STORAGE_BASE_URL if hasattr(settings, 'STORAGE_BASE_URL') else 'https://storage.example.com'
            return f"{base_url}/{key}"
        
        except Exception as e:
            logger.error(f"Error uploading video: {str(e)}")
            raise
    
    @staticmethod
    def upload_image(file_path: str, key: str) -> str:
        """Upload image file to storage and return URL"""
        try:
            # TODO: Implement MinIO/S3 upload
            base_url = settings.STORAGE_BASE_URL if hasattr(settings, 'STORAGE_BASE_URL') else 'https://storage.example.com'
            return f"{base_url}/{key}"
        
        except Exception as e:
            logger.error(f"Error uploading image: {str(e)}")
            raise
    
    @staticmethod
    def upload_image_from_bytes(image_bytes: bytes, filename: str) -> str:
        """Upload image from bytes data to storage"""
        try:
            # TODO: Implement direct bytes upload to MinIO/S3
            base_url = settings.STORAGE_BASE_URL if hasattr(settings, 'STORAGE_BASE_URL') else 'https://storage.example.com'
            return f"{base_url}/images/{filename}"
        
        except Exception as e:
            logger.error(f"Error uploading image from bytes: {str(e)}")
            raise
    
    @staticmethod
    def download_and_upload_image(source_url: str, filename: str) -> str:
        """Download image from URL and upload to storage"""
        try:
            # 이미지 다운로드
            response = requests.get(source_url, timeout=30)
            if response.status_code == 200:
                return StorageService.upload_image_from_bytes(response.content, filename)
            else:
                raise Exception(f"Failed to download image: {response.status_code}")
        
        except Exception as e:
            logger.error(f"Error downloading and uploading image: {str(e)}")
            raise
    
    @staticmethod
    def upload_pdf(pdf_content: bytes, filename: str) -> str:
        """Upload PDF file to storage"""
        try:
            # TODO: Implement PDF upload to MinIO/S3
            base_url = settings.STORAGE_BASE_URL if hasattr(settings, 'STORAGE_BASE_URL') else 'https://storage.example.com'
            return f"{base_url}/documents/{filename}"
        
        except Exception as e:
            logger.error(f"Error uploading PDF: {str(e)}")
            raise
    
    @staticmethod
    def delete_file(key: str) -> bool:
        """Delete file from storage"""
        try:
            # TODO: Implement MinIO/S3 delete
            return True
        
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return False
    
    @staticmethod
    def get_signed_url(key: str, expiry: int = 3600) -> str:
        """Get signed URL for temporary access"""
        try:
            # TODO: Implement MinIO/S3 signed URL generation
            base_url = settings.STORAGE_BASE_URL if hasattr(settings, 'STORAGE_BASE_URL') else 'https://storage.example.com'
            return f"{base_url}/{key}?expires={expiry}"
        
        except Exception as e:
            logger.error(f"Error generating signed URL: {str(e)}")
            raise


class StoryboardGenerationService:
    """
    콘티(스토리보드) 생성을 위한 전용 서비스
    이미지 생성 API와 연동하여 각 씬별 비주얼 콘티 생성
    """
    
    @staticmethod
    def generate_storyboard_for_story(story: Story) -> Dict[str, Any]:
        """스토리 전체에 대한 콘티 생성"""
        try:
            results = []
            total_scenes = story.scenes.count()
            
            for scene in story.scenes.all():
                scene_result = StoryboardGenerationService.generate_scene_storyboard(scene)
                results.append({
                    'scene_id': scene.id,
                    'scene_number': scene.order,
                    'title': scene.title,
                    'result': scene_result
                })
            
            return {
                'success': True,
                'total_scenes': total_scenes,
                'completed_scenes': len([r for r in results if r['result']['success']]),
                'storyboard_data': results
            }
        
        except Exception as e:
            logger.error(f"Error generating storyboard for story {story.id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def generate_scene_storyboard(scene: Scene) -> Dict[str, Any]:
        """개별 씬에 대한 콘티 이미지 생성"""
        try:
            # 선택된 이미지 프롬프트 가져오기
            selected_prompt = scene.prompts.filter(
                prompt_type='image',
                is_selected=True,
                is_active=True
            ).first()
            
            if not selected_prompt:
                return {
                    'success': False,
                    'error': 'No active image prompt found for scene'
                }
            
            # AI 프로바이더 설정 가져오기
            try:
                provider_config = AIProviderConfig.objects.get(
                    provider=scene.story.ai_provider,
                    is_active=True
                )
            except AIProviderConfig.DoesNotExist:
                return {
                    'success': False,
                    'error': f'No active provider config for {scene.story.ai_provider}'
                }
            
            # 콘티 전용 파라미터 설정
            storyboard_params = {
                **selected_prompt.parameters,
                'aspect_ratio': '16:9',  # 스토리보드는 16:9 비율 고정
                'style_preset': 'storyboard',  # 스토리보드 스타일
                'cfg_scale': 6.0,  # 안정적인 생성을 위해 낮은 CFG
                'steps': 25  # 빠른 생성을 위해 단계 수 감소
            }
            
            # 콘티 전용 프롬프트 생성
            storyboard_prompt = StoryboardGenerationService._create_storyboard_prompt(
                selected_prompt.user_prompt, scene
            )
            
            # 이미지 생성 실행
            generation_result = AIProviderIntegration.generate_image(
                provider_config,
                storyboard_prompt,
                storyboard_params
            )
            
            if generation_result['success']:
                # 씬에 스토리보드 URL 저장
                scene.preview_image_url = generation_result['preview_url']
                scene.generation_metadata = {
                    **scene.generation_metadata,
                    'storyboard_generated_at': timezone.now().isoformat(),
                    'storyboard_prompt': storyboard_prompt,
                    'generation_time': generation_result.get('generation_time', 0)
                }
                scene.save()
                
                return {
                    'success': True,
                    'preview_url': generation_result['preview_url'],
                    'generation_time': generation_result.get('generation_time'),
                    'metadata': generation_result.get('metadata', {})
                }
            else:
                return generation_result
        
        except Exception as e:
            logger.error(f"Error generating scene storyboard: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def _create_storyboard_prompt(base_prompt: str, scene: Scene) -> str:
        """스토리보드 전용 프롬프트 생성"""
        # 스토리보드 스타일 접두사
        storyboard_style = "Professional storyboard illustration, clean lineart, cinematic framing"
        
        # 씬 정보 추가
        scene_info = f"Scene {scene.order}: {scene.title}"
        
        # 시간 정보 (타임코드)
        timecode = f"[{scene.start_time:.1f}s - {scene.end_time:.1f}s]"
        
        # 최종 프롬프트 구성
        storyboard_prompt = f"{storyboard_style}. {scene_info} {timecode}. {base_prompt}. Black and white sketch style with clear composition, professional storyboard format"
        
        return storyboard_prompt


class PDFGenerationService:
    """
    PDF 기획안 생성 서비스
    스토리, 콘티, 설정값을 포함한 완전한 기획안 PDF 생성
    """
    
    @staticmethod
    def generate_project_brief(story: Story) -> Dict[str, Any]:
        """프로젝트 기획안 PDF 생성"""
        try:
            # 프로젝트 데이터 수집
            project_data = PDFGenerationService._collect_project_data(story)
            
            # PDF 생성 (실제 구현에서는 ReportLab 등 사용)
            pdf_content = PDFGenerationService._create_pdf_content(project_data)
            
            # 파일 저장 및 URL 생성
            pdf_filename = f"project_brief_{story.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf_url = StorageService.upload_pdf(pdf_content, pdf_filename)
            
            return {
                'success': True,
                'pdf_url': pdf_url,
                'filename': pdf_filename,
                'content_summary': {
                    'total_pages': project_data['page_count'],
                    'sections': project_data['sections'],
                    'scene_count': project_data['scene_count']
                }
            }
        
        except Exception as e:
            logger.error(f"Error generating PDF brief: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def _collect_project_data(story: Story) -> Dict:
        """프로젝트 데이터 수집"""
        project = story.project
        project_data = project.project_data or {} if project else {}
        
        # 스토리 구조 데이터
        story_structure = None
        if project:
            story_dev_result = StoryDevelopmentService.develop_story_from_project(project)
            if story_dev_result['success']:
                story_structure = story_dev_result['story_structure']
        
        # 씬 데이터 수집
        scenes_data = []
        for scene in story.scenes.all():
            scene_data = {
                'number': scene.order,
                'title': scene.title,
                'description': scene.description,
                'duration': scene.duration,
                'start_time': scene.start_time,
                'end_time': scene.end_time,
                'scene_type': scene.scene_type,
                'preview_image_url': scene.preview_image_url,
                'prompts': []
            }
            
            # 프롬프트 정보
            for prompt in scene.prompts.filter(is_active=True):
                scene_data['prompts'].append({
                    'type': prompt.prompt_type,
                    'prompt': prompt.user_prompt,
                    'is_selected': prompt.is_selected,
                    'parameters': prompt.parameters
                })
            
            scenes_data.append(scene_data)
        
        return {
            'story': {
                'id': str(story.id),
                'title': story.title,
                'description': story.description,
                'duration_seconds': story.duration_seconds,
                'resolution': story.resolution,
                'fps': story.fps,
                'status': story.status,
                'created_at': story.created_at
            },
            'project': {
                'id': str(project.id) if project else None,
                'name': project.name if project else 'Unnamed Project',
                'description': project.description if project else '',
                'settings': project_data
            },
            'story_structure': story_structure,
            'scenes': scenes_data,
            'scene_count': len(scenes_data),
            'sections': ['Cover', 'Project Overview', 'Story Structure', 'Scene Breakdown', 'Technical Specifications'],
            'page_count': 5 + len(scenes_data)  # 기본 5페이지 + 씬별 1페이지
        }
    
    @staticmethod
    def _create_pdf_content(project_data: Dict) -> bytes:
        """PDF 내용 생성 (placeholder - 실제로는 ReportLab 사용)"""
        # 실제 구현에서는 ReportLab을 사용하여 PDF 생성
        # 여기서는 간단한 텍스트 기반 내용 생성
        
        pdf_text_content = f"""
        VideoPlanet Project Brief
        ========================
        
        Project: {project_data['project']['name']}
        Story: {project_data['story']['title']}
        Duration: {project_data['story']['duration_seconds']} seconds
        Resolution: {project_data['story']['resolution']}
        FPS: {project_data['story']['fps']}
        
        Story Structure:
        ----------------
        {project_data['story_structure'] if project_data['story_structure'] else 'Standard structure'}
        
        Scene Breakdown:
        ----------------
        """
        
        for scene in project_data['scenes']:
            pdf_text_content += f"""
        Scene {scene['number']}: {scene['title']}
        Duration: {scene['duration']}s ({scene['start_time']}s - {scene['end_time']}s)
        Type: {scene['scene_type']}
        Description: {scene['description']}
        
        """
        
        # 실제로는 이것을 PDF 바이트로 변환
        return pdf_text_content.encode('utf-8')


class AIProviderIntegration:
    """
    Integration layer for AI providers
    Handles API calls to Stability AI, Runway ML, DALL-E etc.
    """
    
    @staticmethod
    def generate_image(config: AIProviderConfig, prompt: str, parameters: Dict) -> Dict:
        """Generate image using AI provider"""
        try:
            # Rate limiting 체크
            if not config.is_within_rate_limits():
                return {
                    'success': False, 
                    'error': 'Rate limit exceeded. Please try again later.'
                }
            
            # 프로바이더별 분기
            if config.provider == AIProvider.STABILITY_AI:
                return AIProviderIntegration._stability_ai_image(config, prompt, parameters)
            elif config.provider == AIProvider.OPENAI:
                return AIProviderIntegration.generate_image_with_dalle(prompt, parameters)
            elif config.provider == AIProvider.RUNWAY_ML:
                return AIProviderIntegration._runway_ml_image(config, prompt, parameters)
            elif config.provider == AIProvider.REPLICATE:
                return AIProviderIntegration._replicate_image(config, prompt, parameters)
            else:
                return {'success': False, 'error': f'Unsupported provider: {config.provider}'}
        
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def generate_video(config: AIProviderConfig, prompt: str, parameters: Dict) -> Dict:
        """Generate video using AI provider"""
        try:
            if config.provider == AIProvider.STABILITY_AI:
                return AIProviderIntegration._stability_ai_video(config, prompt, parameters)
            elif config.provider == AIProvider.RUNWAY_ML:
                return AIProviderIntegration._runway_ml_video(config, prompt, parameters)
            else:
                return {'success': False, 'error': f'Unsupported provider for video: {config.provider}'}
        
        except Exception as e:
            logger.error(f"Error generating video: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def generate_image_with_dalle(prompt: str, parameters: Dict) -> Dict:
        """Generate image using DALL-E 3"""
        try:
            import openai
            
            # DALL-E 3 API 호출
            client = openai.OpenAI(
                api_key=getattr(settings, 'OPENAI_API_KEY', '')
            )
            
            # DALL-E 3 파라미터 설정
            dalle_params = {
                'model': 'dall-e-3',
                'prompt': prompt,
                'size': parameters.get('size', '1792x1024'),  # 16:9 비율
                'quality': parameters.get('quality', 'standard'),  # standard or hd
                'style': parameters.get('style', 'natural'),  # natural or vivid
                'n': 1
            }
            
            response = client.images.generate(**dalle_params)
            
            if response.data:
                image_url = response.data[0].url
                
                # 이미지 다운로드 후 스토리지에 업로드
                final_url = StorageService.download_and_upload_image(image_url, f"dalle_{uuid.uuid4().hex[:8]}.png")
                
                return {
                    'success': True,
                    'preview_url': final_url,
                    'generation_time': 8.5,
                    'metadata': {
                        'provider': 'openai_dalle3',
                        'model': 'dall-e-3',
                        'size': dalle_params['size'],
                        'quality': dalle_params['quality'],
                        'style': dalle_params['style']
                    }
                }
            else:
                return {
                    'success': False,
                    'error': 'No image data received from DALL-E'
                }
        
        except Exception as e:
            logger.error(f"DALL-E error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def _stability_ai_image(config: AIProviderConfig, prompt: str, parameters: Dict) -> Dict:
        """Generate image using Stability AI"""
        try:
            # Stability AI API endpoint - 최신 SDXL 모델 사용
            endpoint = config.api_endpoint or "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
            
            headers = {
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            # Negative prompt 추가 지원
            text_prompts = [{"text": prompt, "weight": 1}]
            if 'negative_prompt' in parameters and parameters['negative_prompt']:
                text_prompts.append({
                    "text": parameters['negative_prompt'],
                    "weight": -1
                })
            
            body = {
                "text_prompts": text_prompts,
                "cfg_scale": parameters.get('cfg_scale', 7),
                "height": parameters.get('height', 1024),
                "width": parameters.get('width', 1024),
                "samples": 1,
                "steps": parameters.get('steps', 30),
                "style_preset": parameters.get('style_preset', 'cinematic'),
                "clip_guidance_preset": parameters.get('clip_guidance_preset', 'FAST_BLUE')
            }
            
            response = requests.post(endpoint, headers=headers, json=body, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                # Extract image data
                image_data = result['artifacts'][0]['base64']
                
                # Base64 이미지를 저장하고 업로드
                import base64
                import io
                from PIL import Image
                
                # Base64 디코딩
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))
                
                # 임시 파일로 저장 후 업로드
                filename = f"stability_{uuid.uuid4().hex[:8]}.png"
                preview_url = StorageService.upload_image_from_bytes(image_bytes, filename)
                
                # 사용량 기록
                config.record_usage(config.cost_per_image)
                
                return {
                    'success': True,
                    'preview_url': preview_url,
                    'generation_time': 5.2,
                    'metadata': {
                        'provider': 'stability_ai',
                        'model': 'sdxl-1.0',
                        'cfg_scale': body['cfg_scale'],
                        'steps': body['steps'],
                        'style_preset': body.get('style_preset')
                    }
                }
            else:
                error_detail = response.json() if response.content else 'Unknown error'
                return {
                    'success': False,
                    'error': f"Stability AI API error: {response.status_code} - {error_detail}"
                }
        
        except requests.exceptions.Timeout:
            return {'success': False, 'error': 'Request timeout'}
        except Exception as e:
            logger.error(f"Stability AI error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def _runway_ml_image(config: AIProviderConfig, prompt: str, parameters: Dict) -> Dict:
        """Generate image using Runway ML"""
        # TODO: Implement Runway ML integration
        return {
            'success': True,
            'preview_url': 'https://placeholder.com/runway_image.png',
            'generation_time': 4.5,
            'metadata': {'provider': 'runway_ml'}
        }
    
    @staticmethod
    def _replicate_image(config: AIProviderConfig, prompt: str, parameters: Dict) -> Dict:
        """Generate image using Replicate"""
        # TODO: Implement Replicate integration
        return {
            'success': True,
            'preview_url': 'https://placeholder.com/replicate_image.png',
            'generation_time': 6.1,
            'metadata': {'provider': 'replicate'}
        }
    
    @staticmethod
    def _stability_ai_video(config: AIProviderConfig, prompt: str, parameters: Dict) -> Dict:
        """Generate video using Stability AI"""
        # TODO: Implement Stability AI video generation
        return {
            'success': True,
            'video_url': 'https://placeholder.com/stability_video.mp4',
            'generation_time': 45.3,
            'metadata': {'provider': 'stability_ai', 'type': 'video'}
        }
    
    @staticmethod
    def _runway_ml_video(config: AIProviderConfig, prompt: str, parameters: Dict) -> Dict:
        """Generate video using Runway ML Gen-2"""
        # TODO: Implement Runway ML Gen-2 integration
        return {
            'success': True,
            'video_url': 'https://placeholder.com/runway_video.mp4',
            'generation_time': 38.7,
            'metadata': {'provider': 'runway_ml', 'model': 'gen2'}
        }