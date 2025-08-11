import logging
from typing import Dict, List, Optional
from django.conf import settings
import google.generativeai as genai
import json
from .video_technical_analyzer import VideoTechnicalAnalyzer, TechnicalIssue

logger = logging.getLogger(__name__)


class AITeacherService:
    """
    AI   
    Twelve Labs      
    """
    
    #   
    TEACHERS = {
        'tiger': {
            'name': ' ',
            'emoji': '',
            'personality': ' ',
            'style': '  ',
            'tone': ' ',
            'greeting': '! ,      !',
            'color': '#FF6B35',
            'bg_color': '#FFF5F0'
        },
        'owl': {
            'name': ' ',
            'emoji': '',
            'personality': ' ',
            'style': '   ',
            'tone': ' ',
            'greeting': '~   .     .',
            'color': '#8B4513',
            'bg_color': '#FFF8DC'
        },
        'fox': {
            'name': ' ',
            'emoji': '',
            'personality': ' ',
            'style': '    ',
            'tone': '  ',
            'greeting': '~   ?      .',
            'color': '#FF7F50',
            'bg_color': '#FFEEEE'
        },
        'bear': {
            'name': ' ',
            'emoji': '',
            'personality': ' ',
            'style': '  ',
            'tone': ' ',
            'greeting': '! ,    .',
            'color': '#8B4513',
            'bg_color': '#F5E6D3'
        }
    }
    
    def __init__(self):
        api_key = getattr(settings, 'GOOGLE_API_KEY', None)
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            logger.warning("Google API key not found")
            self.model = None
        
        #   
        self.technical_analyzer = VideoTechnicalAnalyzer()
    
    def transform_feedback(self, analysis_data: Dict, teacher_type: str) -> Dict:
        """
        Twelve Labs     
        
        Args:
            analysis_data: Twelve Labs  
            teacher_type:   (tiger, owl, fox, bear)
            
        Returns:
             
        """
        if teacher_type not in self.TEACHERS:
            teacher_type = 'owl'  # 
        
        teacher = self.TEACHERS[teacher_type]
        
        try:
            #    
            technical_analysis = self.technical_analyzer.analyze_twelve_labs_data(analysis_data)
            
            # Gemini   
            if self.model:
                feedback = self._generate_teacher_feedback(analysis_data, teacher, technical_analysis)
            else:
                # :   
                feedback = self._generate_fallback_feedback(analysis_data, teacher, technical_analysis)
            
            return {
                'teacher': teacher,
                'feedback': feedback,
                'analysis_summary': self._create_analysis_summary(analysis_data),
                'technical_analysis': technical_analysis
            }
            
        except Exception as e:
            logger.error(f"Error transforming feedback: {e}")
            return self._generate_error_feedback(teacher)
    
    def _generate_teacher_feedback(self, analysis_data: Dict, teacher: Dict, technical_analysis: Dict) -> Dict:
        """Gemini     """
        
        #   
        summary = analysis_data.get('summary', {}).get('text', '')
        key_moments = analysis_data.get('key_moments', [])
        conversations = analysis_data.get('conversations', [])
        texts_in_video = analysis_data.get('text_in_video', [])
        
        #   
        tech_score = technical_analysis.get('overall_score', 70)
        tech_issues = technical_analysis.get('issues', [])
        tech_recommendations = technical_analysis.get('recommendations', [])
        
        prompt = f"""
         '{teacher['name']}'.
        : {teacher['personality']}
         : {teacher['style']}
        : {teacher['tone']}
        
              :
        
        [ ]
         : {tech_score}/100
        
        [  ]
        {self._format_technical_issues(tech_issues)}
        
        [ ]
        {self._format_category_scores(technical_analysis.get('category_scores', {}))}
        
        [  ]
        {summary if summary else '   .'}
        
        [ ]
        {self._format_key_moments(key_moments)}
        
                 :
        1.    ( ,  )
        2.   (     )
        3.   ( 5  )
        4.    (3 , )
        5.   (, , )
        
          JSON :
        {{
            "overall_feedback": "    (2-3)",
            "strengths": ["  1", " 2", " 3"],
            "improvements": [" 1", "2", "3"],
            "specific_comments": [
                {{"timestamp": 10.5, "comment": "//   "}},
                {{"timestamp": 25.3, "comment": "    "}}
            ],
            "final_message": "      ",
            "score": {tech_score},
            "emoji_reaction": ""
        }}
        
        : 
        1.     (, , ,  )  
        2.   ,   
        3.     :
        -  : " 2 !       !"
        -  : "  ,     "
        -  : "~ 3    ?   "
        -  : "       "
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # JSON 
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            feedback_data = json.loads(response_text)
            return feedback_data
            
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            return self._generate_fallback_feedback(analysis_data, teacher, technical_analysis)
    
    def _generate_fallback_feedback(self, analysis_data: Dict, teacher: Dict, technical_analysis: Dict) -> Dict:
        """  """
        
        tech_score = technical_analysis.get('overall_score', 70)
        tech_issues = technical_analysis.get('issues', [])
        
        #    
        templates = {
            'tiger': {
                'overall_feedback': f'  {tech_score}?    !   ,  !',
                'strengths': [
                    '  ',
                    '  ',
                    '   '
                ],
                'improvements': [
                    '  !    !',
                    '  !  !',
                    ' 5 !   !'
                ],
                'final_message': '   !   !',
                'emoji_reaction': ''
            },
            'owl': {
                'overall_feedback': f'  {tech_score}.        .',
                'strengths': [
                    '    ',
                    '   ',
                    '  '
                ],
                'improvements': [
                    '   .      ',
                    '     ',
                    '       ?'
                ],
                'final_message': '      .  !',
                'emoji_reaction': ''
            },
            'fox': {
                'overall_feedback': f'~ {tech_score}?    ?        ?',
                'strengths': [
                    ' ,   ',
                    '  ',
                    '    '
                ],
                'improvements': [
                    '3  ?   ',
                    ' ,   ?',
                    ' 5    '
                ],
                'final_message': '   ,    . ~',
                'emoji_reaction': ''
            },
            'bear': {
                'overall_feedback': f'  {tech_score}   .   .',
                'strengths': [
                    '    ',
                    '    ',
                    '     '
                ],
                'improvements': [
                    '    .     ',
                    '        ',
                    ' 5      '
                ],
                'final_message': '    .  !',
                'emoji_reaction': ''
            }
        }
        
        template = templates.get(teacher['name'].split()[0].lower(), templates['owl'])
        
        #      
        specific_comments = []
        
        #      
        for issue in tech_issues[:3]:
            if issue.timestamp is not None:
                comment_templates = {
                    'tiger': f"! {issue.timestamp:.1f}  {issue.description}    !",
                    'owl': f"{issue.timestamp:.1f}   {issue.description}    .",
                    'fox': f", {issue.timestamp:.1f} {issue.description}   .",
                    'bear': f"{issue.timestamp:.1f}  {issue.description}   ."
                }
                
                teacher_key = teacher['name'].split()[0].lower()
                specific_comments.append({
                    'timestamp': issue.timestamp,
                    'comment': comment_templates.get(teacher_key, comment_templates['owl'])
                })
        
        #   key_moments 
        if not specific_comments and analysis_data.get('key_moments'):
            for i, moment in enumerate(analysis_data['key_moments'][:2]):
                specific_comments.append({
                    'timestamp': moment.get('start_time', i * 10),
                    'comment': f"     ."
                })
        
        return {
            'overall_feedback': template['overall_feedback'],
            'strengths': template['strengths'],
            'improvements': template['improvements'],
            'specific_comments': specific_comments,
            'final_message': template['final_message'],
            'score': tech_score,
            'emoji_reaction': template['emoji_reaction']
        }
    
    def _generate_error_feedback(self, teacher: Dict) -> Dict:
        """   """
        return {
            'teacher': teacher,
            'feedback': {
                'overall_feedback': f"{teacher['emoji']}    .  .",
                'strengths': [],
                'improvements': [],
                'specific_comments': [],
                'final_message': '     .',
                'score': 0,
                'emoji_reaction': ''
            },
            'analysis_summary': {}
        }
    
    def _format_key_moments(self, moments: List[Dict]) -> str:
        """  """
        if not moments:
            return "   "
        
        formatted = []
        for i, moment in enumerate(moments[:5]):
            formatted.append(f"- {moment['start_time']:.1f}:  ")
        return '\n'.join(formatted)
    
    def _format_conversations(self, conversations: List[Dict]) -> str:
        """  """
        if not conversations:
            return "  "
        
        formatted = []
        for conv in conversations[:5]:
            formatted.append(f"- [{conv['start_time']:.1f}s] {conv['transcript'][:50]}...")
        return '\n'.join(formatted)
    
    def _format_texts(self, texts: List[Dict]) -> str:
        """  """
        if not texts:
            return "  "
        
        formatted = []
        for text in texts[:5]:
            formatted.append(f"- [{text['start_time']:.1f}s] {text['text']}")
        return '\n'.join(formatted)
    
    def _create_analysis_summary(self, analysis_data: Dict) -> Dict:
        """  """
        return {
            'total_key_moments': len(analysis_data.get('key_moments', [])),
            'total_conversations': len(analysis_data.get('conversations', [])),
            'total_texts': len(analysis_data.get('text_in_video', [])),
            'has_summary': bool(analysis_data.get('summary', {}).get('text'))
        }
    
    def get_all_teachers(self) -> Dict:
        """   """
        return self.TEACHERS
    
    def _format_technical_issues(self, issues: List) -> str:
        """  """
        if not issues:
            return "    ."
        
        formatted = []
        for issue in issues[:5]:  #  5
            severity_emoji = {
                'critical': '',
                'major': '',
                'minor': 'ℹ',
                'info': ''
            }.get(issue.severity, '•')
            
            formatted.append(f"{severity_emoji} [{issue.category}] {issue.description}")
        
        return '\n'.join(formatted)
    
    def _format_category_scores(self, category_scores: Dict) -> str:
        """  """
        if not category_scores:
            return "   "
        
        formatted = []
        for cat_key, cat_data in category_scores.items():
            score = cat_data.get('score', 0)
            name = cat_data.get('name', cat_key)
            emoji = '' if score >= 80 else '' if score >= 60 else ''
            formatted.append(f"{emoji} {name}: {score}/100")
        
        return '\n'.join(formatted)