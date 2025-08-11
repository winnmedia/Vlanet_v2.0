"""
      
"""
import json
import logging
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import transaction
from django.utils import timezone
from users.utils import user_validator
from . import models

logger = logging.getLogger(__name__)


class ProjectScheduleManager:
    """      """
    
    PHASE_ORDER = [
        'basic_plan',
        'story_board',
        'filming',
        'video_edit',
        'post_work',
        'video_preview',
        'confirmation',
        'video_delivery'
    ]
    
    PHASE_MODEL_MAP = {
        'basic_plan': models.BasicPlan,
        'story_board': models.Storyboard,
        'filming': models.Filming,
        'video_edit': models.VideoEdit,
        'post_work': models.PostWork,
        'video_preview': models.VideoPreview,
        'confirmation': models.Confirmation,
        'video_delivery': models.VideoDelivery,
    }
    
    @classmethod
    def update_phase_schedule(cls, project, phase_key, start_date, end_date, completed=None):
        """   """
        if phase_key not in cls.PHASE_MODEL_MAP:
            raise ValueError(f"Invalid phase key: {phase_key}")
        
        #  
        if isinstance(start_date, str):
            start_date = cls._parse_date(start_date)
        if isinstance(end_date, str):
            end_date = cls._parse_date(end_date)
        
        #     
        phase_obj = getattr(project, phase_key)
        
        if phase_obj is None:
            #    
            PhaseModel = cls.PHASE_MODEL_MAP[phase_key]
            phase_obj = PhaseModel.objects.create(
                start_date=start_date,
                end_date=end_date
            )
            setattr(project, phase_key, phase_obj)
            project.save()
        else:
            #   
            phase_obj.start_date = start_date
            phase_obj.end_date = end_date
            
            # completed    (   )
            if completed is not None and hasattr(phase_obj, 'completed'):
                phase_obj.completed = completed
            
            phase_obj.save()
        
        return phase_obj
    
    @classmethod
    def adjust_subsequent_phases(cls, project, completed_phase_key, actual_completion_date=None):
        """       """
        if completed_phase_key not in cls.PHASE_ORDER:
            raise ValueError(f"Invalid phase key: {completed_phase_key}")
        
        completed_index = cls.PHASE_ORDER.index(completed_phase_key)
        if completed_index >= len(cls.PHASE_ORDER) - 1:
            #     
            return []
        
        #   
        if actual_completion_date is None:
            actual_completion_date = timezone.now()
        elif isinstance(actual_completion_date, str):
            actual_completion_date = cls._parse_date(actual_completion_date)
        
        #     
        completed_phase = getattr(project, completed_phase_key)
        if not completed_phase or not completed_phase.end_date:
            return []
        
        # /  
        original_end = completed_phase.end_date
        if timezone.is_naive(original_end):
            original_end = timezone.make_aware(original_end)
        if timezone.is_naive(actual_completion_date):
            actual_completion_date = timezone.make_aware(actual_completion_date)
        
        days_diff = (actual_completion_date.date() - original_end.date()).days
        
        if days_diff == 0:
            return []  #  
        
        #   
        adjusted_phases = []
        for i in range(completed_index + 1, len(cls.PHASE_ORDER)):
            phase_key = cls.PHASE_ORDER[i]
            phase_obj = getattr(project, phase_key)
            
            if phase_obj and phase_obj.start_date and phase_obj.end_date:
                #   
                new_start = phase_obj.start_date + timedelta(days=days_diff)
                new_end = phase_obj.end_date + timedelta(days=days_diff)
                
                # 
                phase_obj.start_date = new_start
                phase_obj.end_date = new_end
                phase_obj.save()
                
                adjusted_phases.append({
                    'phase': phase_key,
                    'new_start': new_start,
                    'new_end': new_end,
                    'adjustment_days': days_diff
                })
        
        return adjusted_phases
    
    @staticmethod
    def _parse_date(date_string):
        """   """
        if not date_string:
            return None
        
        #   
        date_formats = [
            '%Y-%m-%d %H:%M',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S.%fZ',
        ]
        
        for fmt in date_formats:
            try:
                dt = datetime.strptime(date_string, fmt)
                # timezone aware 
                if timezone.is_naive(dt):
                    dt = timezone.make_aware(dt)
                return dt
            except ValueError:
                continue
        
        raise ValueError(f"Unable to parse date: {date_string}")


@method_decorator(csrf_exempt, name='dispatch')
class ProjectScheduleUpdate(View):
    """     """
    
    @user_validator
    @transaction.atomic
    def post(self, request, project_id):
        try:
            user = request.user
            
            #  
            try:
                project = models.Project.objects.get(id=project_id)
            except models.Project.DoesNotExist:
                return JsonResponse({
                    "success": False,
                    "message": "   ."
                }, status=404)
            
            #  
            is_manager = models.Members.objects.filter(
                project=project, 
                user=user, 
                rating="manager"
            ).exists()
            
            if project.user != user and not is_manager:
                return JsonResponse({
                    "success": False,
                    "message": "    ."
                }, status=403)
            
            #   
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({
                    "success": False,
                    "message": " JSON ."
                }, status=400)
            
            phase_key = data.get("key")
            start_date = data.get("start_date")
            end_date = data.get("end_date")
            completed = data.get("completed")
            auto_adjust = data.get("auto_adjust", False)  #     
            
            #   
            if not phase_key:
                return JsonResponse({
                    "success": False,
                    "message": " (key) ."
                }, status=400)
            
            if not start_date or not end_date:
                return JsonResponse({
                    "success": False,
                    "message": "  ."
                }, status=400)
            
            #  
            try:
                phase_obj = ProjectScheduleManager.update_phase_schedule(
                    project, phase_key, start_date, end_date, completed
                )
                
                response_data = {
                    "success": True,
                    "message": " .",
                    "phase": {
                        "key": phase_key,
                        "start_date": phase_obj.start_date.isoformat(),
                        "end_date": phase_obj.end_date.isoformat()
                    }
                }
                
                #       
                if completed and auto_adjust:
                    adjusted = ProjectScheduleManager.adjust_subsequent_phases(
                        project, phase_key
                    )
                    if adjusted:
                        response_data["adjusted_phases"] = adjusted
                        response_data["message"] = f"  {len(adjusted)}   ."
                
                return JsonResponse(response_data, status=200)
                
            except ValueError as e:
                return JsonResponse({
                    "success": False,
                    "message": str(e)
                }, status=400)
            
        except Exception as e:
            logger.error(f"Error in ProjectScheduleUpdate: {str(e)}", exc_info=True)
            return JsonResponse({
                "success": False,
                "message": "    .",
                "error": str(e) if settings.DEBUG else None
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ProjectScheduleBulkUpdate(View):
    """     """
    
    @user_validator
    @transaction.atomic
    def post(self, request, project_id):
        try:
            user = request.user
            
            #     ( )
            try:
                project = models.Project.objects.get(id=project_id)
            except models.Project.DoesNotExist:
                return JsonResponse({
                    "success": False,
                    "message": "   ."
                }, status=404)
            
            is_manager = models.Members.objects.filter(
                project=project, 
                user=user, 
                rating="manager"
            ).exists()
            
            if project.user != user and not is_manager:
                return JsonResponse({
                    "success": False,
                    "message": "    ."
                }, status=403)
            
            #   
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({
                    "success": False,
                    "message": " JSON ."
                }, status=400)
            
            phases_data = data.get("phases", [])
            if not phases_data:
                return JsonResponse({
                    "success": False,
                    "message": "   ."
                }, status=400)
            
            #   
            updated_phases = []
            for phase_data in phases_data:
                phase_key = phase_data.get("key")
                start_date = phase_data.get("start_date")
                end_date = phase_data.get("end_date")
                completed = phase_data.get("completed")
                
                if not phase_key or not start_date or not end_date:
                    continue
                
                try:
                    phase_obj = ProjectScheduleManager.update_phase_schedule(
                        project, phase_key, start_date, end_date, completed
                    )
                    updated_phases.append({
                        "key": phase_key,
                        "start_date": phase_obj.start_date.isoformat(),
                        "end_date": phase_obj.end_date.isoformat()
                    })
                except Exception as e:
                    logger.error(f"Error updating phase {phase_key}: {str(e)}")
            
            return JsonResponse({
                "success": True,
                "message": f"{len(updated_phases)}  .",
                "updated_phases": updated_phases
            }, status=200)
            
        except Exception as e:
            logger.error(f"Error in ProjectScheduleBulkUpdate: {str(e)}", exc_info=True)
            return JsonResponse({
                "success": False,
                "message": "    .",
                "error": str(e) if settings.DEBUG else None
            }, status=500)