"""
   
 ,  ,  
"""

from django.utils import timezone
from datetime import timedelta
from .models import *
import json
import statistics

class AnalyticsProcessor:
    """     """
    
    def __init__(self):
        self.insight_thresholds = {
            'long_step_duration': {
                1: 600000,  # 10
                2: 300000,  # 5
                3: 360000,  # 6
                4: 480000   # 8
            },
            'high_edit_count': 5,
            'high_clear_count': 3,
            'high_abandonment_rate': 0.3
        }
    
    def process_real_time_event(self, event):
        """  """
        session = event.session
        
        #   
        if event.event_type == 'step_enter':
            self._process_step_entry(session, event)
        elif event.event_type == 'form_interaction':
            self._process_form_interaction(session, event)
        elif event.event_type == 'generation_start':
            self._process_generation_start(session, event)
        elif event.event_type == 'error_occurred':
            self._process_error(session, event)
        
        #   
        self._generate_real_time_insights(session)
    
    def _process_step_entry(self, session, event):
        """  """
        step = event.data.get('step')
        if not step:
            return
        
        #    
        previous_step = step - 1
        if previous_step > 0:
            previous_metrics = PerformanceMetric.objects.filter(
                session=session, step=previous_step
            ).first()
            
            if previous_metrics and previous_metrics.step_duration > self.insight_thresholds['long_step_duration'].get(previous_step, 600000):
                self._create_insight(
                    session,
                    'time_warning',
                    'high',
                    f' {previous_step}    .',
                    'show_ai_assistant'
                )
    
    def _process_form_interaction(self, session, event):
        """  """
        field_name = event.data.get('fieldName')
        action = event.data.get('action')
        
        if action == 'clear' and field_name:
            #    
            interaction, created = FormInteraction.objects.get_or_create(
                session=session,
                field_name=field_name,
                defaults={'clear_count': 1}
            )
            
            if not created:
                interaction.clear_count += 1
                interaction.save()
                
                #    
                if interaction.clear_count >= self.insight_thresholds['high_clear_count']:
                    self._create_insight(
                        session,
                        'content_struggle',
                        'medium',
                        f'{field_name}      .  ?',
                        'show_templates'
                    )
    
    def _process_generation_start(self, session, event):
        """  """
        generation_type = event.data.get('type')
        
        #    ()
        if generation_type == 'storyboard':
            self._create_insight(
                session,
                'generation_delay',
                'low',
                '  .  .',
                'show_progress'
            )
    
    def _process_error(self, session, event):
        """ """
        error_type = event.data.get('errorType')
        error_message = event.data.get('errorMessage')
        
        self._create_insight(
            session,
            'error_occurred',
            'high',
            f' : {error_message}',
            'contact_support'
        )
    
    def _generate_real_time_insights(self, session):
        """  """
        current_time = timezone.now()
        
        #    
        session_duration = (current_time - session.start_time).total_seconds() * 1000
        
        if session_duration > 1800000:  # 30 
            existing_insight = UserInsight.objects.filter(
                session=session,
                insight_type='abandonment_risk',
                resolved=False
            ).first()
            
            if not existing_insight:
                self._create_insight(
                    session,
                    'abandonment_risk',
                    'high',
                    '   .   ?',
                    'suggest_save'
                )
        
        #    
        self._analyze_form_patterns(session)
        
        #   
        self._analyze_click_patterns(session)
    
    def _analyze_form_patterns(self, session):
        """   """
        form_interactions = FormInteraction.objects.filter(session=session)
        
        for interaction in form_interactions:
            #    
            if interaction.change_count >= self.insight_thresholds['high_edit_count']:
                self._create_insight(
                    session,
                    'high_edit_count',
                    'medium',
                    f'{interaction.field_name}    .    ?',
                    'show_examples'
                )
            
            #   
            if interaction.abandonment_rate >= self.insight_thresholds['high_abandonment_rate']:
                self._create_insight(
                    session,
                    'content_struggle',
                    'medium',
                    f'{interaction.field_name}      .',
                    'show_ai_assistant'
                )
    
    def _analyze_click_patterns(self, session):
        """  """
        clicks = ClickHeatmap.objects.filter(session=session)
        
        #    
        regenerate_clicks = clicks.filter(
            button_type__icontains='regenerate'
        ).aggregate(total=models.Sum('click_count'))['total'] or 0
        
        if regenerate_clicks >= 5:
            self._create_insight(
                session,
                'generation_dissatisfaction',
                'medium',
                '   ?    .',
                'improve_prompts'
            )
    
    def _create_insight(self, session, insight_type, severity, message, action_suggestion):
        """ """
        #  :       
        existing = UserInsight.objects.filter(
            session=session,
            insight_type=insight_type,
            resolved=False
        ).first()
        
        if existing:
            return
        
        UserInsight.objects.create(
            session=session,
            insight_type=insight_type,
            severity=severity,
            message=message,
            action_suggestion=action_suggestion
        )
    
    def generate_daily_analytics(self, date=None):
        """   """
        if not date:
            date = timezone.now().date()
        
        sessions = UserSession.objects.filter(start_time__date=date)
        total_sessions = sessions.count()
        
        if total_sessions == 0:
            return
        
        #  
        total_users = sessions.filter(user__isnull=False).values('user').distinct().count()
        average_duration = sessions.aggregate(
            avg=models.Avg('duration')
        )['avg'] or 0
        average_duration_minutes = average_duration / 1000 / 60
        
        #  
        completion_rate = sessions.aggregate(
            avg=models.Avg('completion_rate')
        )['avg'] or 0
        
        #  
        step_completions = {}
        for step in range(1, 5):
            count = sessions.filter(final_step__gte=step).count()
            step_completions[f'step_{step}_completion'] = (
                count / total_sessions * 100 if total_sessions > 0 else 0
            )
        
        #   
        step_durations = {}
        for step in range(1, 5):
            avg_duration = PerformanceMetric.objects.filter(
                session__start_time__date=date,
                step=step
            ).aggregate(avg=models.Avg('step_duration'))['avg'] or 0
            step_durations[f'average_step_{step}_duration'] = avg_duration / 1000 / 60
        
        #  
        total_errors = UserEvent.objects.filter(
            timestamp__date=date,
            event_type='error_occurred'
        ).count()
        
        #  
        most_clicked_button = ClickHeatmap.objects.filter(
            session__start_time__date=date
        ).values('button_type').annotate(
            total=models.Sum('click_count')
        ).order_by('-total').first()
        
        most_edited_field = FormInteraction.objects.filter(
            session__start_time__date=date
        ).values('field_name').annotate(
            total=models.Sum('change_count')
        ).order_by('-total').first()
        
        #     
        daily_analytics, created = DailyAnalytics.objects.get_or_create(
            date=date,
            defaults={
                'total_sessions': total_sessions,
                'total_users': total_users,
                'average_session_duration': average_duration_minutes,
                'completion_rate': completion_rate,
                'step_1_completion': step_completions['step_1_completion'],
                'step_2_completion': step_completions['step_2_completion'],
                'step_3_completion': step_completions['step_3_completion'],
                'step_4_completion': step_completions['step_4_completion'],
                'average_step_1_duration': step_durations['average_step_1_duration'],
                'average_step_2_duration': step_durations['average_step_2_duration'],
                'average_step_3_duration': step_durations['average_step_3_duration'],
                'average_step_4_duration': step_durations['average_step_4_duration'],
                'total_errors': total_errors,
                'most_clicked_button': most_clicked_button['button_type'] if most_clicked_button else '',
                'most_edited_field': most_edited_field['field_name'] if most_edited_field else '',
            }
        )
        
        if not created:
            # 
            daily_analytics.total_sessions = total_sessions
            daily_analytics.total_users = total_users
            daily_analytics.average_session_duration = average_duration_minutes
            daily_analytics.completion_rate = completion_rate
            daily_analytics.step_1_completion = step_completions['step_1_completion']
            daily_analytics.step_2_completion = step_completions['step_2_completion']
            daily_analytics.step_3_completion = step_completions['step_3_completion']
            daily_analytics.step_4_completion = step_completions['step_4_completion']
            daily_analytics.total_errors = total_errors
            daily_analytics.most_clicked_button = most_clicked_button['button_type'] if most_clicked_button else ''
            daily_analytics.most_edited_field = most_edited_field['field_name'] if most_edited_field else ''
            daily_analytics.save()
        
        return daily_analytics
    
    def get_optimization_recommendations(self, session_id):
        """  """
        try:
            session = UserSession.objects.get(session_id=session_id)
        except UserSession.DoesNotExist:
            return []
        
        recommendations = []
        
        #    
        metrics = PerformanceMetric.objects.filter(session=session)
        for metric in metrics:
            if metric.efficiency_score < 50:
                recommendations.append({
                    'type': 'efficiency',
                    'priority': 'high',
                    'message': f' {metric.step}  . AI   .',
                    'action': 'enable_ai_assistant'
                })
            
            if metric.frustration_score > 60:
                recommendations.append({
                    'type': 'frustration',
                    'priority': 'high',
                    'message': f' {metric.step}     .  .',
                    'action': 'suggest_templates'
                })
        
        #    
        form_interactions = FormInteraction.objects.filter(session=session)
        for interaction in form_interactions:
            if interaction.clear_count > 2:
                recommendations.append({
                    'type': 'content_help',
                    'priority': 'medium',
                    'message': f'{interaction.field_name}   .',
                    'action': 'show_examples'
                })
        
        return recommendations
    
    def predict_user_needs(self, session_id):
        """  """
        try:
            session = UserSession.objects.get(session_id=session_id)
        except UserSession.DoesNotExist:
            return []
        
        predictions = []
        current_time = timezone.now()
        session_duration = (current_time - session.start_time).total_seconds() * 1000
        
        #   
        if session_duration > 900000 and session.final_step == 1:  # 15  1
            predictions.append({
                'need': 'content_inspiration',
                'confidence': 0.85,
                'suggestion': 'AI       '
            })
        
        if session.final_step == 4:  #  
            recent_regenerations = ClickHeatmap.objects.filter(
                session=session,
                button_type__icontains='regenerate'
            ).aggregate(total=models.Sum('click_count'))['total'] or 0
            
            if recent_regenerations > 3:
                predictions.append({
                    'need': 'better_prompts',
                    'confidence': 0.9,
                    'suggestion': '     '
                })
        
        return predictions