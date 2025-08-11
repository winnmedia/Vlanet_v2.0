"""
  
     
"""
import logging
from django.db import transaction, IntegrityError
from django.utils import timezone
from . import models

logger = logging.getLogger(__name__)


class ProjectCreationError(Exception):
    """    """
    pass


def create_project_atomic(user, project_data, processes):
    """
      
         
    """
    with transaction.atomic():
        #   SELECT FOR UPDATE  
        user_locked = models.User.objects.select_for_update().get(pk=user.pk)
        
        #    ( )
        duplicate_check = models.Project.objects.filter(
            user=user_locked,
            name=project_data['name'],
            created__gte=timezone.now() - timezone.timedelta(seconds=30)
        ).exists()
        
        if duplicate_check:
            raise ProjectCreationError(
                "    ."
            )
        
        try:
            #  
            project = models.Project.objects.create(
                user=user_locked,
                name=project_data['name'],
                manager=project_data.get('manager', ''),
                consumer=project_data.get('consumer', ''),
                description=project_data.get('description', ''),
                color=project_data.get('color', '#1631F8'),
                tone_manner=project_data.get('tone_manner', ''),
                genre=project_data.get('genre', ''),
                concept=project_data.get('concept', '')
            )
            
            #  
            for process_data in processes:
                models.Process.objects.create(
                    project=project,
                    key=process_data['key'],
                    start_date=process_data['start_date'],
                    end_date=process_data['end_date'],
                    is_complete=False
                )
            
            #   
            feedback = models.FeedBack.objects.create(
                project=project,
                user=user_locked,
                name=f"{project.name} "
            )
            
            #   
            project.feedback = feedback
            project.save()
            
            logger.info(f"Successfully created project '{project.name}' with ID: {project.id}")
            return project
            
        except IntegrityError as e:
            logger.error(f"Integrity error creating project: {e}")
            raise ProjectCreationError(
                "      ."
            )
        except Exception as e:
            logger.error(f"Unexpected error creating project: {e}")
            raise ProjectCreationError(
                f"    : {str(e)}"
            )


def update_project_atomic(project_id, user, update_data):
    """
      
    """
    with transaction.atomic():
        try:
            # SELECT FOR UPDATE  
            project = models.Project.objects.select_for_update().get(
                id=project_id,
                user=user
            )
            
            #    
            updatable_fields = [
                'name', 'manager', 'consumer', 'description', 
                'color', 'tone_manner', 'genre', 'concept'
            ]
            
            for field in updatable_fields:
                if field in update_data:
                    setattr(project, field, update_data[field])
            
            project.save()
            
            logger.info(f"Successfully updated project {project_id}")
            return project
            
        except models.Project.DoesNotExist:
            raise ProjectCreationError("   .")
        except Exception as e:
            logger.error(f"Error updating project {project_id}: {e}")
            raise ProjectCreationError(
                f"    : {str(e)}"
            )


def delete_project_atomic(project_id, user):
    """
      
        
    """
    with transaction.atomic():
        try:
            # SELECT FOR UPDATE  
            project = models.Project.objects.select_for_update().get(
                id=project_id,
                user=user
            )
            
            #    CASCADE  
            project_name = project.name
            project.delete()
            
            logger.info(f"Successfully deleted project '{project_name}' (ID: {project_id})")
            return True
            
        except models.Project.DoesNotExist:
            raise ProjectCreationError("   .")
        except Exception as e:
            logger.error(f"Error deleting project {project_id}: {e}")
            raise ProjectCreationError(
                f"    : {str(e)}"
            )