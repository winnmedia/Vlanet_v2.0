"""
AI    - 1000%     
"""
import json
import time
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from django.conf import settings
from django.utils import timezone
from .models import VideoPlanning, VideoPlanningAIPrompt

logger = logging.getLogger(__name__)

@dataclass
class PromptGenerationContext:
    """  """
    planning: VideoPlanning
    prompt_type: str
    user_input: str
    pro_options: Dict[str, Any]
    context_data: Dict[str, Any]
    optimization_level: str = 'high'  # low, medium, high, extreme

@dataclass
class PromptGenerationResult:
    """  """
    original_prompt: str
    enhanced_prompt: str
    generation_time: float
    tokens_estimate: int
    cost_estimate: float
    confidence_score: float
    optimization_suggestions: List[str]
    is_successful: bool
    error_message: str = ""

class AIPromptEngine:
    """AI    -   """
    
    def __init__(self):
        self.prompt_templates = self._load_prompt_templates()
        self.optimization_rules = self._load_optimization_rules()
        self.context_enhancers = self._load_context_enhancers()
        
    def _load_prompt_templates(self) -> Dict[str, Dict]:
        """  """
        return {
            'story': {
                'base': "  .   : {planning_text}",
                'professional': """
                   .
                
                ****: {planning_text}
                ****: {genre}
                ****: {tone_manner}
                ** **: {target_audience}
                ** **: {key_message}
                
                ****:
                -  , ,  
                -    
                -    
                - /  
                """,
                'creative': """
                    .
                
                ** **: {planning_text}
                ** **: {creative_concept}
                ** **: {visual_style}
                ** **: {innovation_elements}
                
                ** **:
                -    
                -    
                -   
                -    
                """
            },
            'scene': {
                'professional': """
                      :
                
                ** **: {selected_story}
                ** **: {camera_settings}
                ** **: {lighting_setup}
                **/**: {location_setting}
                
                **  **:
                -    
                -     
                -    
                - /  
                -     
                """
            },
            'shot': {
                'professional': """
                      :
                
                ** **: {selected_scene}
                ** **: {camera_specs}
                ** **: {budget_range}
                
                **  **:
                -     
                -    (, , )
                -    
                -   
                -  
                """
            },
            'image': {
                'storyboard': """
                    DALL-E :
                
                ** **: {scene_description}
                ** **: {visual_style}
                ** **: {color_palette}
                ****: {mood}
                ** **: {camera_angle}
                
                **  **:
                - 16:9   
                -   
                -   
                -    
                
                : "Professional storyboard illustration, {scene_description}, {visual_style} style, {color_palette} color scheme, {mood} atmosphere, {camera_angle} camera angle, 16:9 aspect ratio, clean composition, cinematic lighting"
                """
            }
        }
    
    def _load_optimization_rules(self) -> Dict[str, List]:
        """  """
        return {
            'clarity_enhancers': [
                '   ',
                '  ',
                '   ',
                '   '
            ],
            'creativity_boosters': [
                '   ',
                '   ',
                '   ',
                '  '
            ],
            'efficiency_optimizers': [
                '   ',
                '   ',
                '   ',
                '   '
            ]
        }
    
    def _load_context_enhancers(self) -> Dict[str, callable]:
        """  """
        return {
            'brand_integration': self._enhance_brand_context,
            'technical_specs': self._enhance_technical_context,
            'creative_direction': self._enhance_creative_context,
            'budget_optimization': self._enhance_budget_context
        }
    
    def generate_enhanced_prompt(self, context: PromptGenerationContext) -> PromptGenerationResult:
        """  """
        start_time = time.time()
        
        try:
            # 1.   
            base_prompt = self._select_base_prompt(context)
            
            # 2.     
            enhanced_context = self._enhance_context(context)
            
            # 3.  
            optimized_prompt = self._optimize_prompt(base_prompt, enhanced_context, context.optimization_level)
            
            # 4.  
            quality_score = self._validate_prompt_quality(optimized_prompt)
            
            # 5.   
            generation_time = time.time() - start_time
            tokens_estimate = self._estimate_tokens(optimized_prompt)
            cost_estimate = self._estimate_cost(tokens_estimate)
            
            # 6.   
            suggestions = self._generate_optimization_suggestions(context, optimized_prompt)
            
            # 7.  
            self._save_prompt_record(context, base_prompt, optimized_prompt, generation_time, tokens_estimate, cost_estimate, True)
            
            return PromptGenerationResult(
                original_prompt=base_prompt,
                enhanced_prompt=optimized_prompt,
                generation_time=generation_time,
                tokens_estimate=tokens_estimate,
                cost_estimate=cost_estimate,
                confidence_score=quality_score,
                optimization_suggestions=suggestions,
                is_successful=True
            )
            
        except Exception as e:
            logger.error(f"  : {str(e)}")
            generation_time = time.time() - start_time
            
            #   
            self._save_prompt_record(context, context.user_input, "", generation_time, 0, 0, False, str(e))
            
            return PromptGenerationResult(
                original_prompt=context.user_input,
                enhanced_prompt="",
                generation_time=generation_time,
                tokens_estimate=0,
                cost_estimate=0,
                confidence_score=0,
                optimization_suggestions=[],
                is_successful=False,
                error_message=str(e)
            )
    
    def _select_base_prompt(self, context: PromptGenerationContext) -> str:
        """  """
        prompt_type = context.prompt_type
        optimization_level = context.optimization_level
        
        if prompt_type in self.prompt_templates:
            templates = self.prompt_templates[prompt_type]
            
            if optimization_level in ['high', 'extreme'] and 'professional' in templates:
                return templates['professional']
            elif optimization_level == 'medium' and 'creative' in templates:
                return templates.get('creative', templates.get('professional', templates['base']))
            else:
                return templates.get('base', templates[list(templates.keys())[0]])
        
        #  
        return f"{context.user_input}  {prompt_type} ."
    
    def _enhance_context(self, context: PromptGenerationContext) -> Dict[str, Any]:
        """  """
        enhanced = context.context_data.copy()
        planning = context.planning
        
        #   
        enhanced.update({
            'planning_text': planning.planning_text,
            'title': planning.title,
            'current_step': planning.current_step,
            'planning_options': planning.planning_options,
        })
        
        #    (color_tone  )
        # if planning.color_tone:
        #     enhanced['color_palette'] = planning.color_tone
        #     enhanced['primary_color'] = planning.color_tone.get('primary', '#1631F8')
        #     enhanced['mood'] = planning.color_tone.get('mood', 'professional')
        
        #  
        # if planning.camera_settings:
        #     enhanced['camera_settings'] = planning.camera_settings
        #     enhanced['camera_specs'] = planning.get_camera_specs()
        #     enhanced['camera_angle'] = planning.camera_settings.get('shot_type', 'medium')
        
        # if planning.lighting_setup:
        #     enhanced['lighting_setup'] = planning.lighting_setup
        #     enhanced['lighting_mood'] = planning.lighting_setup.get('mood', 'professional')
        
        # if planning.audio_config:
        #     enhanced['audio_config'] = planning.audio_config
        #     enhanced['bgm_style'] = planning.audio_config.get('bgm_style', 'corporate')
        
        #   
        if planning.selected_story:
            enhanced['selected_story'] = json.dumps(planning.selected_story, ensure_ascii=False)
        
        if planning.selected_scene:
            enhanced['selected_scene'] = json.dumps(planning.selected_scene, ensure_ascii=False)
        
        #    
        for enhancer_name, enhancer_func in self.context_enhancers.items():
            try:
                enhanced = enhancer_func(enhanced, context)
            except Exception as e:
                logger.warning(f"   ({enhancer_name}): {str(e)}")
        
        return enhanced
    
    def _optimize_prompt(self, base_prompt: str, context: Dict[str, Any], optimization_level: str) -> str:
        """ """
        optimized = base_prompt
        
        #   
        try:
            optimized = optimized.format(**context)
        except KeyError as e:
            logger.warning(f"   : {str(e)}")
            #    
            for key in e.args:
                context[key] = f"[{key}  ]"
            optimized = optimized.format(**context)
        
        #    
        if optimization_level in ['high', 'extreme']:
            optimized = self._apply_clarity_rules(optimized)
            optimized = self._apply_efficiency_rules(optimized)
        
        if optimization_level == 'extreme':
            optimized = self._apply_creativity_rules(optimized)
            optimized = self._apply_advanced_optimization(optimized)
        
        return optimized
    
    def _apply_clarity_rules(self, prompt: str) -> str:
        """  """
        #   
        if '' in prompt and ' ' not in prompt:
            prompt += "\n\n** **: JSON    ."
        
        #   
        if '' in prompt:
            prompt += "\n** **:   ,   ,    ."
        
        return prompt
    
    def _apply_efficiency_rules(self, prompt: str) -> str:
        """  """
        #   
        if '' in prompt:
            prompt += "\n** **:           ."
        
        return prompt
    
    def _apply_creativity_rules(self, prompt: str) -> str:
        """  """
        #   
        if '' in prompt or '' in prompt:
            prompt += "\n** **:         ."
        
        return prompt
    
    def _apply_advanced_optimization(self, prompt: str) -> str:
        """  """
        #   
        prompt += f"\n\n** **:  ({timezone.now().strftime('%Y %m')})     ."
        
        #   
        prompt += "\n** **:            ."
        
        return prompt
    
    def _enhance_brand_context(self, context: Dict[str, Any], planning_context: PromptGenerationContext) -> Dict[str, Any]:
        """  """
        #      
        planning = planning_context.planning
        if hasattr(planning, 'user') and planning.user:
            context['brand_context'] = {
                'user_style': '',
                'brand_values': ['', '', ''],
                'target_market': ' '
            }
        return context
    
    def _enhance_technical_context(self, context: Dict[str, Any], planning_context: PromptGenerationContext) -> Dict[str, Any]:
        """  """
        #   
        if 'camera_settings' in context:
            camera = context['camera_settings']
            context['technical_requirements'] = {
                'video_codec': 'H.264/H.265',
                'audio_codec': 'AAC',
                'bitrate': ' (50-100Mbps)',
                'color_space': 'Rec.709'
            }
        return context
    
    def _enhance_creative_context(self, context: Dict[str, Any], planning_context: PromptGenerationContext) -> Dict[str, Any]:
        """  """
        #   
        context['creative_inspiration'] = [
            '   ',
            ' ',
            ' ',
            ' '
        ]
        return context
    
    def _enhance_budget_context(self, context: Dict[str, Any], planning_context: PromptGenerationContext) -> Dict[str, Any]:
        """  """
        #   
        context['budget_considerations'] = {
            'cost_effective_alternatives': True,
            'resource_optimization': True,
            'scalable_solutions': True
        }
        return context
    
    def _validate_prompt_quality(self, prompt: str) -> float:
        """  """
        score = 0.0
        
        #   ( )
        if 100 <= len(prompt) <= 2000:
            score += 20
        
        #  
        if '**' in prompt or '#' in prompt:
            score += 15
        
        #  
        specific_terms = ['', '', '', '', '']
        score += sum(10 for term in specific_terms if term in prompt)
        
        #  
        action_terms = ['', '', '', '', '']
        score += sum(5 for term in action_terms if term in prompt)
        
        return min(score, 100.0)
    
    def _estimate_tokens(self, prompt: str) -> int:
        """  """
        #    ( tokenizer )
        return len(prompt.split()) * 1.3  #    
    
    def _estimate_cost(self, tokens: int) -> float:
        """ """
        # GPT-4    ( API  )
        cost_per_1k_tokens = 0.03  # USD
        return (tokens / 1000) * cost_per_1k_tokens
    
    def _generate_optimization_suggestions(self, context: PromptGenerationContext, prompt: str) -> List[str]:
        """  """
        suggestions = []
        
        #   
        if len(prompt) < 200:
            suggestions.append("          .")
        elif len(prompt) > 1500:
            suggestions.append("    AI   .")
        
        #   
        if context.optimization_level == 'low':
            suggestions.append("  'high'       .")
        
        #    
        if not context.planning.is_pro_mode_enabled():
            suggestions.append("          .")
        
        return suggestions
    
    def _save_prompt_record(self, context: PromptGenerationContext, original: str, enhanced: str, 
                          generation_time: float, tokens: int, cost: float, success: bool, error: str = ""):
        """  """
        try:
            VideoPlanningAIPrompt.objects.create(
                planning=context.planning,
                prompt_type=context.prompt_type,
                original_prompt=original,
                enhanced_prompt=enhanced,
                generation_time=generation_time,
                tokens_used=int(tokens),
                cost_estimate=cost,
                is_successful=success,
                error_message=error
            )
        except Exception as e:
            logger.error(f"   : {str(e)}")

class PromptOptimizationService:
    """  """
    
    def __init__(self):
        self.engine = AIPromptEngine()
    
    def generate_story_prompt(self, planning: VideoPlanning, user_input: str, optimization_level: str = 'high') -> PromptGenerationResult:
        """  """
        context = PromptGenerationContext(
            planning=planning,
            prompt_type='story',
            user_input=user_input,
            pro_options=self._extract_pro_options(planning),
            context_data={},
            optimization_level=optimization_level
        )
        return self.engine.generate_enhanced_prompt(context)
    
    def generate_scene_prompt(self, planning: VideoPlanning, user_input: str, optimization_level: str = 'high') -> PromptGenerationResult:
        """  """
        context = PromptGenerationContext(
            planning=planning,
            prompt_type='scene',
            user_input=user_input,
            pro_options=self._extract_pro_options(planning),
            context_data={},
            optimization_level=optimization_level
        )
        return self.engine.generate_enhanced_prompt(context)
    
    def generate_shot_prompt(self, planning: VideoPlanning, user_input: str, optimization_level: str = 'high') -> PromptGenerationResult:
        """  """
        context = PromptGenerationContext(
            planning=planning,
            prompt_type='shot',
            user_input=user_input,
            pro_options=self._extract_pro_options(planning),
            context_data={},
            optimization_level=optimization_level
        )
        return self.engine.generate_enhanced_prompt(context)
    
    def generate_image_prompt(self, planning: VideoPlanning, scene_description: str, optimization_level: str = 'high') -> PromptGenerationResult:
        """   """
        context = PromptGenerationContext(
            planning=planning,
            prompt_type='image',
            user_input=scene_description,
            pro_options=self._extract_pro_options(planning),
            context_data={'scene_description': scene_description},
            optimization_level=optimization_level
        )
        return self.engine.generate_enhanced_prompt(context)
    
    def _extract_pro_options(self, planning: VideoPlanning) -> Dict[str, Any]:
        """  """
        return {
            #  
            # 'color_tone': planning.color_tone,
            # 'camera_settings': planning.camera_settings,
            # 'lighting_setup': planning.lighting_setup,
            # 'audio_config': planning.audio_config,
            # 'ai_generation_config': planning.ai_generation_config
        }
    
    def get_optimization_analytics(self, planning: VideoPlanning) -> Dict[str, Any]:
        """   """
        prompts = VideoPlanningAIPrompt.objects.filter(planning=planning)
        
        if not prompts.exists():
            return {'message': '  .'}
        
        total_prompts = prompts.count()
        successful_prompts = prompts.filter(is_successful=True).count()
        avg_generation_time = prompts.aggregate(avg_time=models.Avg('generation_time'))['avg_time'] or 0
        total_cost = prompts.aggregate(total=models.Sum('cost_estimate'))['total'] or 0
        
        return {
            'total_prompts': total_prompts,
            'success_rate': (successful_prompts / total_prompts) * 100,
            'avg_generation_time': round(avg_generation_time, 2),
            'total_cost': float(total_cost),
            'efficiency_rating': self._calculate_efficiency_rating(successful_prompts, total_prompts, avg_generation_time),
            'recommendations': self._generate_recommendations(planning, prompts)
        }
    
    def _calculate_efficiency_rating(self, successful: int, total: int, avg_time: float) -> str:
        """  """
        success_rate = (successful / total) * 100 if total > 0 else 0
        
        if success_rate >= 95 and avg_time <= 2:
            return 'excellent'
        elif success_rate >= 85 and avg_time <= 5:
            return 'good'
        elif success_rate >= 70:
            return 'average'
        else:
            return 'needs_improvement'
    
    def _generate_recommendations(self, planning: VideoPlanning, prompts) -> List[str]:
        """  """
        recommendations = []
        
        #   
        success_rate = prompts.filter(is_successful=True).count() / prompts.count() * 100
        if success_rate < 80:
            recommendations.append("   'extreme' .")
        
        #   
        avg_cost = prompts.aggregate(avg=models.Avg('cost_estimate'))['avg'] or 0
        if avg_cost > 0.1:
            recommendations.append("      .")
        
        #   
        if not planning.is_pro_mode_enabled():
            recommendations.append("        .")
        
        return recommendations