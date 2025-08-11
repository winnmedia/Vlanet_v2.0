"""
   
       
"""
import logging
import json
import threading
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass
from enum import Enum
from contextlib import contextmanager
from django.db import transaction, connection
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings
from .error_tracking import error_tracker, ErrorSeverity, ErrorCategory, ErrorContext

logger = logging.getLogger('data_consistency')

class ConsistencyLevel(Enum):
    """ """
    EVENTUAL = "eventual"    #  
    STRONG = "strong"        #  
    WEAK = "weak"           #  

class OperationType(Enum):
    """ """
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    BULK_UPDATE = "bulk_update"
    SYNC = "sync"

@dataclass
class ConsistencyRule:
    """ """
    name: str
    models: List[str]  #  
    level: ConsistencyLevel
    dependencies: List[str]  #  
    validators: List[Callable]  #  
    auto_repair: bool = True  #   
    priority: int = 1  #  (1  )

@dataclass
class DataOperation:
    """ """
    operation_id: str
    operation_type: OperationType
    model_name: str
    instance_id: Optional[int]
    data: Dict[str, Any]
    user_id: Optional[int]
    timestamp: str
    dependencies: List[str] = None
    consistency_level: ConsistencyLevel = ConsistencyLevel.STRONG

@dataclass
class ConsistencyViolation:
    """ """
    violation_id: str
    rule_name: str
    model_name: str
    instance_id: Optional[int]
    description: str
    severity: str
    detected_at: str
    resolved: bool = False
    resolution_method: Optional[str] = None

class DataConsistencyManager:
    """  """
    
    def __init__(self):
        self.consistency_rules: Dict[str, ConsistencyRule] = {}
        self.pending_operations: List[DataOperation] = []
        self.violations: List[ConsistencyViolation] = []
        self.lock = threading.Lock()
        self._initialize_consistency_rules()
    
    def _initialize_consistency_rules(self):
        """   """
        
        #     
        self.add_consistency_rule(ConsistencyRule(
            name="video_planning_integrity",
            models=["VideoPlanning", "VideoPlanningImage", "VideoPlanningAIPrompt"],
            level=ConsistencyLevel.STRONG,
            dependencies=["User"],
            validators=[self._validate_video_planning_integrity],
            auto_repair=True,
            priority=1
        ))
        
        # - 
        self.add_consistency_rule(ConsistencyRule(
            name="project_feedback_consistency",
            models=["Project", "Feedback", "FeedbackComment"],
            level=ConsistencyLevel.STRONG,
            dependencies=["User", "Members"],
            validators=[self._validate_project_feedback_consistency],
            auto_repair=True,
            priority=1
        ))
        
        # - 
        self.add_consistency_rule(ConsistencyRule(
            name="user_permission_consistency",
            models=["User", "Members", "VideoPlanningCollaboration"],
            level=ConsistencyLevel.STRONG,
            dependencies=[],
            validators=[self._validate_user_permission_consistency],
            auto_repair=True,
            priority=2
        ))
        
        # -DB 
        self.add_consistency_rule(ConsistencyRule(
            name="cache_database_consistency",
            models=["*"],  #  
            level=ConsistencyLevel.EVENTUAL,
            dependencies=[],
            validators=[self._validate_cache_database_consistency],
            auto_repair=True,
            priority=3
        ))
    
    def add_consistency_rule(self, rule: ConsistencyRule):
        """  """
        self.consistency_rules[rule.name] = rule
        logger.info(f"  : {rule.name}")
    
    @contextmanager
    def atomic_operation(self, operation: DataOperation):
        """  """
        with self.lock:
            self.pending_operations.append(operation)
        
        try:
            with transaction.atomic():
                #  
                self._pre_validate_operation(operation)
                
                yield
                
                #  
                self._post_validate_operation(operation)
                
                #   
                self._invalidate_related_cache(operation)
                
                logger.info(f"  : {operation.operation_id}")
                
        except Exception as e:
            logger.error(f"  : {operation.operation_id} - {str(e)}")
            
            #  
            context = ErrorContext(
                user_id=operation.user_id,
                additional_data={
                    'operation_id': operation.operation_id,
                    'operation_type': operation.operation_type.value,
                    'model_name': operation.model_name
                }
            )
            error_tracker.track_error(e, ErrorSeverity.HIGH, ErrorCategory.DATABASE, context)
            
            raise
        finally:
            with self.lock:
                if operation in self.pending_operations:
                    self.pending_operations.remove(operation)
    
    def _pre_validate_operation(self, operation: DataOperation):
        """  """
        applicable_rules = self._get_applicable_rules(operation.model_name)
        
        for rule in applicable_rules:
            if rule.level == ConsistencyLevel.STRONG:
                for validator in rule.validators:
                    try:
                        validator(operation, pre_validation=True)
                    except Exception as e:
                        logger.error(f"   ({rule.name}): {str(e)}")
                        raise
    
    def _post_validate_operation(self, operation: DataOperation):
        """  """
        applicable_rules = self._get_applicable_rules(operation.model_name)
        
        for rule in applicable_rules:
            for validator in rule.validators:
                try:
                    validator(operation, pre_validation=False)
                except Exception as e:
                    if rule.auto_repair:
                        logger.warning(f"  ,    ({rule.name}): {str(e)}")
                        try:
                            self._attempt_auto_repair(rule, operation, e)
                        except Exception as repair_error:
                            logger.error(f"   ({rule.name}): {str(repair_error)}")
                            self._record_violation(rule, operation, str(e))
                            raise
                    else:
                        logger.error(f"   ({rule.name}): {str(e)}")
                        self._record_violation(rule, operation, str(e))
                        raise
    
    def _get_applicable_rules(self, model_name: str) -> List[ConsistencyRule]:
        """   """
        applicable_rules = []
        
        for rule in self.consistency_rules.values():
            if "*" in rule.models or model_name in rule.models:
                applicable_rules.append(rule)
        
        #   
        applicable_rules.sort(key=lambda r: r.priority)
        return applicable_rules
    
    def _invalidate_related_cache(self, operation: DataOperation):
        """  """
        try:
            #    
            cache_patterns = [
                f"{operation.model_name.lower()}:*",
                f"user:{operation.user_id}:*" if operation.user_id else None,
                f"{operation.model_name.lower()}:{operation.instance_id}:*" if operation.instance_id else None,
            ]
            
            for pattern in cache_patterns:
                if pattern:
                    self._invalidate_cache_pattern(pattern)
            
        except Exception as e:
            logger.warning(f"  : {str(e)}")
    
    def _invalidate_cache_pattern(self, pattern: str):
        """   """
        try:
            # Redis  
            from django_redis import get_redis_connection
            redis_conn = get_redis_connection("default")
            
            keys = redis_conn.keys(pattern)
            if keys:
                redis_conn.delete(*keys)
                logger.debug(f"  {len(keys)} : {pattern}")
                
        except ImportError:
            # Redis     
            cache.clear()
            logger.debug("  ")
        except Exception as e:
            logger.warning(f"  : {str(e)}")
    
    def _record_violation(self, rule: ConsistencyRule, operation: DataOperation, description: str):
        """  """
        violation = ConsistencyViolation(
            violation_id=f"{rule.name}_{operation.operation_id}_{timezone.now().timestamp()}",
            rule_name=rule.name,
            model_name=operation.model_name,
            instance_id=operation.instance_id,
            description=description,
            severity="high" if rule.level == ConsistencyLevel.STRONG else "medium",
            detected_at=timezone.now().isoformat()
        )
        
        self.violations.append(violation)
        
        #   (24)
        cache.set(f"consistency_violation:{violation.violation_id}", violation, 86400)
        
        logger.error(f"  : {violation.violation_id}")
    
    def _attempt_auto_repair(self, rule: ConsistencyRule, operation: DataOperation, error: Exception):
        """  """
        repair_method = f"_repair_{rule.name}"
        
        if hasattr(self, repair_method):
            repair_function = getattr(self, repair_method)
            repair_function(operation, error)
            logger.info(f"  : {rule.name}")
        else:
            logger.warning(f"   : {rule.name}")
            raise error
    
    #  
    def _validate_video_planning_integrity(self, operation: DataOperation, pre_validation: bool = False):
        """   """
        if operation.model_name == "VideoPlanning":
            if not pre_validation:  #  
                #    
                from video_planning.models import VideoPlanning
                
                try:
                    planning = VideoPlanning.objects.get(id=operation.instance_id)
                    
                    #   
                    if not planning.title or not planning.planning_text:
                        raise ValueError("    .")
                    
                    #   
                    if not planning.user:
                        raise ValueError("    .")
                    
                    # JSON   
                    if planning.planning_options and not isinstance(planning.planning_options, dict):
                        raise ValueError("    .")
                    
                except VideoPlanning.DoesNotExist:
                    if operation.operation_type != OperationType.DELETE:
                        raise ValueError(f"  {operation.instance_id}   .")
    
    def _validate_project_feedback_consistency(self, operation: DataOperation, pre_validation: bool = False):
        """-  """
        if operation.model_name in ["Project", "Feedback", "FeedbackComment"]:
            if not pre_validation:
                #      
                if operation.model_name == "Feedback" and operation.instance_id:
                    from feedbacks.models import Feedback
                    from projects.models import Project
                    
                    try:
                        feedback = Feedback.objects.get(id=operation.instance_id)
                        
                        #    (   )
                        # feedback project   
                        if hasattr(feedback, 'project') and feedback.project:
                            if not Project.objects.filter(id=feedback.project.id).exists():
                                raise ValueError("   .")
                        
                    except Feedback.DoesNotExist:
                        if operation.operation_type != OperationType.DELETE:
                            raise ValueError(f" {operation.instance_id}   .")
    
    def _validate_user_permission_consistency(self, operation: DataOperation, pre_validation: bool = False):
        """   """
        if operation.model_name in ["User", "Members", "VideoPlanningCollaboration"]:
            if not pre_validation and operation.user_id:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                
                #   
                if not User.objects.filter(id=operation.user_id).exists():
                    raise ValueError(f" {operation.user_id}  .")
                
                #   
                if operation.model_name == "VideoPlanningCollaboration":
                    from video_planning.models import VideoPlanningCollaboration, VideoPlanning
                    
                    if operation.instance_id:
                        try:
                            collaboration = VideoPlanningCollaboration.objects.get(id=operation.instance_id)
                            
                            #   
                            if not VideoPlanning.objects.filter(id=collaboration.planning.id).exists():
                                raise ValueError("    .")
                            
                            #   
                            if not User.objects.filter(id=collaboration.user.id).exists():
                                raise ValueError("   .")
                            
                        except VideoPlanningCollaboration.DoesNotExist:
                            if operation.operation_type != OperationType.DELETE:
                                raise ValueError(f" {operation.instance_id}   .")
    
    def _validate_cache_database_consistency(self, operation: DataOperation, pre_validation: bool = False):
        """-  """
        if not pre_validation:  #  
            #   DB  
            cache_key = f"{operation.model_name.lower()}:{operation.instance_id}"
            cached_data = cache.get(cache_key)
            
            if cached_data and operation.operation_type in [OperationType.UPDATE, OperationType.DELETE]:
                #   
                logger.debug(f"  : {cache_key}  ")
    
    #   
    def _repair_video_planning_integrity(self, operation: DataOperation, error: Exception):
        """   """
        from video_planning.models import VideoPlanning
        
        try:
            planning = VideoPlanning.objects.get(id=operation.instance_id)
            
            #   
            if not planning.title and planning.planning_text:
                planning.title = planning.planning_text[:50] + "..." if len(planning.planning_text) > 50 else planning.planning_text
            
            #  
            if not planning.planning_options:
                planning.planning_options = {}
            
            planning.save()
            logger.info(f"  {operation.instance_id}   ")
            
        except Exception as e:
            logger.error(f"    : {str(e)}")
            raise
    
    def _repair_project_feedback_consistency(self, operation: DataOperation, error: Exception):
        """-  """
        #   ,    
        logger.info(f"-   : {operation.instance_id}")
        #     
    
    def _repair_user_permission_consistency(self, operation: DataOperation, error: Exception):
        """   """
        logger.info(f"    : {operation.instance_id}")
        #     
    
    def _repair_cache_database_consistency(self, operation: DataOperation, error: Exception):
        """-  """        
        #   
        self._invalidate_related_cache(operation)
        logger.info(f"-   : {operation.model_name}")
    
    def check_global_consistency(self) -> Dict[str, Any]:
        """  """
        consistency_report = {
            'timestamp': timezone.now().isoformat(),
            'rules_checked': len(self.consistency_rules),
            'violations_found': 0,
            'violations_resolved': 0,
            'rules_status': {},
            'recommendations': []
        }
        
        for rule_name, rule in self.consistency_rules.items():
            rule_status = {
                'rule_name': rule_name,
                'level': rule.level.value,
                'models': rule.models,
                'violations': [],
                'status': 'healthy'
            }
            
            try:
                #      
                violations = self._check_rule_globally(rule)
                
                if violations:
                    rule_status['violations'] = violations
                    rule_status['status'] = 'violations_found'
                    consistency_report['violations_found'] += len(violations)
                    
                    #   
                    if rule.auto_repair:
                        resolved_count = self._attempt_global_repair(rule, violations)
                        consistency_report['violations_resolved'] += resolved_count
                
            except Exception as e:
                rule_status['status'] = 'check_failed'
                rule_status['error'] = str(e)
                logger.error(f"    ({rule_name}): {str(e)}")
            
            consistency_report['rules_status'][rule_name] = rule_status
        
        #  
        if consistency_report['violations_found'] > 0:
            consistency_report['recommendations'].append("    .")
        
        if consistency_report['violations_found'] > 10:
            consistency_report['recommendations'].append("   .")
        
        return consistency_report
    
    def _check_rule_globally(self, rule: ConsistencyRule) -> List[Dict[str, Any]]:
        """  """
        violations = []
        
        #      
        if rule.name == "video_planning_integrity":
            violations.extend(self._check_video_planning_integrity_globally())
        elif rule.name == "project_feedback_consistency":
            violations.extend(self._check_project_feedback_consistency_globally())
        elif rule.name == "user_permission_consistency":
            violations.extend(self._check_user_permission_consistency_globally())
        
        return violations
    
    def _check_video_planning_integrity_globally(self) -> List[Dict[str, Any]]:
        """    """
        violations = []
        
        try:
            from video_planning.models import VideoPlanning
            
            #    
            plannings_missing_title = VideoPlanning.objects.filter(title__isnull=True).or_(
                VideoPlanning.objects.filter(title__exact='')
            )
            
            for planning in plannings_missing_title:
                violations.append({
                    'type': 'missing_title',
                    'instance_id': planning.id,
                    'description': f'  {planning.id}  .',
                    'severity': 'medium'
                })
            
            #    
            plannings_missing_user = VideoPlanning.objects.filter(user__isnull=True)
            
            for planning in plannings_missing_user:
                violations.append({
                    'type': 'missing_user',
                    'instance_id': planning.id,
                    'description': f'  {planning.id}   .',
                    'severity': 'high'
                })
            
        except Exception as e:
            logger.error(f"     : {str(e)}")
        
        return violations
    
    def _check_project_feedback_consistency_globally(self) -> List[Dict[str, Any]]:
        """-   """
        violations = []
        
        try:
            #    
            #      
            pass
            
        except Exception as e:
            logger.error(f"-    : {str(e)}")
        
        return violations
    
    def _check_user_permission_consistency_globally(self) -> List[Dict[str, Any]]:
        """    """
        violations = []
        
        try:
            from video_planning.models import VideoPlanningCollaboration
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            #     
            collaborations = VideoPlanningCollaboration.objects.select_related('user')
            
            for collab in collaborations:
                if not User.objects.filter(id=collab.user.id).exists():
                    violations.append({
                        'type': 'invalid_user_reference',
                        'instance_id': collab.id,
                        'description': f' {collab.id}    .',
                        'severity': 'high'
                    })
            
        except Exception as e:
            logger.error(f"     : {str(e)}")
        
        return violations
    
    def _attempt_global_repair(self, rule: ConsistencyRule, violations: List[Dict[str, Any]]) -> int:
        """  """
        resolved_count = 0
        
        for violation in violations:
            try:
                if self._repair_violation(rule, violation):
                    resolved_count += 1
                    
            except Exception as e:
                logger.error(f"   ({violation}): {str(e)}")
        
        return resolved_count
    
    def _repair_violation(self, rule: ConsistencyRule, violation: Dict[str, Any]) -> bool:
        """  """
        try:
            if rule.name == "video_planning_integrity":
                return self._repair_video_planning_violation(violation)
            elif rule.name == "project_feedback_consistency":
                return self._repair_project_feedback_violation(violation)
            elif rule.name == "user_permission_consistency":
                return self._repair_user_permission_violation(violation)
            
            return False
            
        except Exception as e:
            logger.error(f"  : {str(e)}")
            return False
    
    def _repair_video_planning_violation(self, violation: Dict[str, Any]) -> bool:
        """   """
        from video_planning.models import VideoPlanning
        
        try:
            planning = VideoPlanning.objects.get(id=violation['instance_id'])
            
            if violation['type'] == 'missing_title':
                if planning.planning_text:
                    planning.title = planning.planning_text[:50] + "..." if len(planning.planning_text) > 50 else planning.planning_text
                else:
                    planning.title = f"  {planning.id}"
                
                planning.save()
                return True
            
        except VideoPlanning.DoesNotExist:
            logger.warning(f"     : {violation['instance_id']}")
        
        return False
    
    def _repair_project_feedback_violation(self, violation: Dict[str, Any]) -> bool:
        """-  """
        #     
        return False
    
    def _repair_user_permission_violation(self, violation: Dict[str, Any]) -> bool:
        """   """
        #     
        return False

#     
data_consistency_manager = DataConsistencyManager()

# 
def ensure_data_consistency(model_name: str, 
                          operation_type: OperationType,
                          consistency_level: ConsistencyLevel = ConsistencyLevel.STRONG):
    """   """
    def decorator(func):
        def wrapper(*args, **kwargs):
            #     
            request = None
            for arg in args:
                if hasattr(arg, 'user'):
                    request = arg
                    break
            
            user_id = request.user.id if request and hasattr(request, 'user') and request.user.is_authenticated else None
            
            #   
            operation = DataOperation(
                operation_id=f"{func.__name__}_{timezone.now().timestamp()}",
                operation_type=operation_type,
                model_name=model_name,
                instance_id=None,  #    
                data={},
                user_id=user_id,
                timestamp=timezone.now().isoformat(),
                consistency_level=consistency_level
            )
            
            #    
            with data_consistency_manager.atomic_operation(operation):
                result = func(*args, **kwargs)
                
                #   ID  ( )
                if hasattr(result, 'id'):
                    operation.instance_id = result.id
                elif hasattr(result, 'data') and isinstance(result.data, dict) and 'id' in result.data:
                    operation.instance_id = result.data['id']
                
                return result
        
        return wrapper
    return decorator