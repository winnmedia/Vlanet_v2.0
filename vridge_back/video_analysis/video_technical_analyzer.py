"""
    
/, ,     
"""
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)


@dataclass
class TechnicalIssue:
    """  """
    category: str  # 'horizon', 'eye_level', 'highlight', 'composition', 'lighting'
    severity: str  # 'critical', 'major', 'minor', 'info'
    description: str
    timestamp: Optional[float] = None
    suggestions: Optional[List[str]] = None


class VideoTechnicalAnalyzer:
    """
        
    """
    
    #   
    ANALYSIS_CATEGORIES = {
        'horizon': {
            'name': '  ',
            'weight': 0.25,
            'checks': [
                'horizontal_alignment',  #  
                'camera_tilt',          #  
                'perspective_distortion' #  
            ]
        },
        'eye_level': {
            'name': ' ',
            'weight': 0.25,
            'checks': [
                'shot_consistency',      #   
                'character_eye_level',   #  
                'camera_height'          #  
            ]
        },
        'highlight': {
            'name': ' ',
            'weight': 0.20,
            'checks': [
                'opening_impact',        #  
                'highlight_placement',   #  
                'attention_grabbing'     #  
            ]
        },
        'composition': {
            'name': '  ',
            'weight': 0.15,
            'checks': [
                'rule_of_thirds',        # 3 
                'headroom',              # 
                'lead_space',            #  
                'balance'                # 
            ]
        },
        'technical_quality': {
            'name': ' ',
            'weight': 0.15,
            'checks': [
                'focus_sharpness',       #  
                'exposure',              # 
                'color_consistency',     #  
                'stabilization'          #  
            ]
        }
    }
    
    def analyze_twelve_labs_data(self, twelve_labs_data: Dict) -> Dict:
        """
        Twelve Labs      
        """
        try:
            analysis_result = {
                'overall_score': 0,
                'category_scores': {},
                'issues': [],
                'technical_summary': {},
                'recommendations': []
            }
            
            #   
            for category_key, category_info in self.ANALYSIS_CATEGORIES.items():
                category_score, category_issues = self._analyze_category(
                    category_key, 
                    category_info, 
                    twelve_labs_data
                )
                
                analysis_result['category_scores'][category_key] = {
                    'name': category_info['name'],
                    'score': category_score,
                    'weight': category_info['weight']
                }
                
                analysis_result['issues'].extend(category_issues)
            
            #    ( )
            total_score = sum(
                score_data['score'] * score_data['weight'] 
                for score_data in analysis_result['category_scores'].values()
            )
            analysis_result['overall_score'] = round(total_score)
            
            #   
            analysis_result['technical_summary'] = self._generate_technical_summary(
                analysis_result['category_scores'],
                analysis_result['issues']
            )
            
            #   
            analysis_result['recommendations'] = self._generate_recommendations(
                analysis_result['issues']
            )
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Technical analysis error: {e}")
            return self._get_default_analysis()
    
    def _analyze_category(self, category_key: str, category_info: Dict, 
                         twelve_labs_data: Dict) -> tuple:
        """  """
        issues = []
        base_score = 100
        
        # Twelve Labs    
        visual_data = twelve_labs_data.get('summary', {})
        key_moments = twelve_labs_data.get('key_moments', [])
        
        if category_key == 'horizon':
            issues.extend(self._check_horizon_issues(visual_data, key_moments))
        elif category_key == 'eye_level':
            issues.extend(self._check_eye_level_consistency(key_moments))
        elif category_key == 'highlight':
            issues.extend(self._check_highlight_placement(key_moments))
        elif category_key == 'composition':
            issues.extend(self._check_composition_quality(visual_data, key_moments))
        elif category_key == 'technical_quality':
            issues.extend(self._check_technical_quality(visual_data))
        
        #      
        for issue in issues:
            if issue.severity == 'critical':
                base_score -= 20
            elif issue.severity == 'major':
                base_score -= 10
            elif issue.severity == 'minor':
                base_score -= 5
        
        return max(0, base_score), issues
    
    def _check_horizon_issues(self, visual_data: Dict, key_moments: List) -> List[TechnicalIssue]:
        """   """
        issues = []
        
        #  Twelve Labs visual analysis     
        #  
        if len(key_moments) > 0:
            #     
            if key_moments[0].get('start_time', 0) < 3:
                issues.append(TechnicalIssue(
                    category='horizon',
                    severity='major',
                    description='    ',
                    timestamp=0,
                    suggestions=[
                        '     ',
                        '    '
                    ]
                ))
        
        return issues
    
    def _check_eye_level_consistency(self, key_moments: List) -> List[TechnicalIssue]:
        """  """
        issues = []
        
        #      
        if len(key_moments) >= 2:
            for i in range(1, min(len(key_moments), 5)):
                # :     
                issues.append(TechnicalIssue(
                    category='eye_level',
                    severity='minor',
                    description=f'{i}      ',
                    timestamp=key_moments[i].get('start_time'),
                    suggestions=[
                        '       ',
                        '     '
                    ]
                ))
        
        return issues
    
    def _check_highlight_placement(self, key_moments: List) -> List[TechnicalIssue]:
        """  """
        issues = []
        
        #  5   
        has_early_highlight = any(
            moment.get('start_time', 0) < 5 
            for moment in key_moments[:3]
        )
        
        if not has_early_highlight:
            issues.append(TechnicalIssue(
                category='highlight',
                severity='critical',
                description='  5     ',
                timestamp=0,
                suggestions=[
                    '      ',
                    ' 3        ',
                    '    '
                ]
            ))
        
        return issues
    
    def _check_composition_quality(self, visual_data: Dict, key_moments: List) -> List[TechnicalIssue]:
        """    """
        issues = []
        
        #    
        issues.append(TechnicalIssue(
            category='composition',
            severity='minor',
            description='  3   ',
            suggestions=[
                '  3   ',
                ' 3   '
            ]
        ))
        
        return issues
    
    def _check_technical_quality(self, visual_data: Dict) -> List[TechnicalIssue]:
        """  """
        issues = []
        
        #   
        issues.append(TechnicalIssue(
            category='technical_quality',
            severity='minor',
            description='   ',
            suggestions=[
                '  ',
                '     '
            ]
        ))
        
        return issues
    
    def _generate_technical_summary(self, category_scores: Dict, issues: List) -> Dict:
        """   """
        critical_issues = [i for i in issues if i.severity == 'critical']
        major_issues = [i for i in issues if i.severity == 'major']
        
        return {
            'total_issues': len(issues),
            'critical_issues': len(critical_issues),
            'major_issues': len(major_issues),
            'weakest_category': min(category_scores.items(), 
                                   key=lambda x: x[1]['score'])[0],
            'strongest_category': max(category_scores.items(), 
                                    key=lambda x: x[1]['score'])[0]
        }
    
    def _generate_recommendations(self, issues: List[TechnicalIssue]) -> List[Dict]:
        """   """
        recommendations = []
        
        #  
        critical_issues = [i for i in issues if i.severity == 'critical']
        major_issues = [i for i in issues if i.severity == 'major']
        
        #   
        category_recommendations = {}
        for issue in critical_issues + major_issues:
            if issue.category not in category_recommendations:
                category_recommendations[issue.category] = {
                    'category': self.ANALYSIS_CATEGORIES.get(issue.category, {}).get('name', issue.category),
                    'priority': 'high' if issue.severity == 'critical' else 'medium',
                    'suggestions': []
                }
            
            if issue.suggestions:
                category_recommendations[issue.category]['suggestions'].extend(issue.suggestions)
        
        #    
        for category_data in category_recommendations.values():
            category_data['suggestions'] = list(set(category_data['suggestions']))[:3]
            recommendations.append(category_data)
        
        return sorted(recommendations, key=lambda x: x['priority'], reverse=True)
    
    def _get_default_analysis(self) -> Dict:
        """   ( )"""
        return {
            'overall_score': 70,
            'category_scores': {
                category_key: {
                    'name': category_info['name'],
                    'score': 70,
                    'weight': category_info['weight']
                }
                for category_key, category_info in self.ANALYSIS_CATEGORIES.items()
            },
            'issues': [],
            'technical_summary': {
                'total_issues': 0,
                'critical_issues': 0,
                'major_issues': 0
            },
            'recommendations': []
        }