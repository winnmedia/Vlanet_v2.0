"""
  
"""
from django.contrib.auth import get_user_model
from . import models
from users.models import Notification
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

class NotificationService:
    """ """
    
    NOTIFICATION_TYPES = {
        'INVITATION_RECEIVED': {
            'title': ' ',
            'icon': '',
            'color': '#1631F8'
        },
        'INVITATION_ACCEPTED': {
            'title': ' ',
            'icon': '',
            'color': '#28a745'
        },
        'INVITATION_DECLINED': {
            'title': ' ',
            'icon': '',
            'color': '#dc3545'
        },
        'MEMBER_JOINED': {
            'title': '  ',
            'icon': '',
            'color': '#17a2b8'
        },
        'MEMBER_LEFT': {
            'title': ' ',
            'icon': '',
            'color': '#ffc107'
        },
        'PROJECT_UPDATED': {
            'title': ' ',
            'icon': '',
            'color': '#6c757d'
        },
        'FEEDBACK_RECEIVED': {
            'title': ' ',
            'icon': '',
            'color': '#fd7e14'
        }
    }
    
    @staticmethod
    def create_notification(user, notification_type, title, message, related_object=None, action_url=None):
        """ """
        try:
            notification_config = NotificationService.NOTIFICATION_TYPES.get(notification_type, {})
            
            notification = Notification.objects.create(
                recipient=user,
                notification_type=notification_type.lower(),
                title=title,
                message=message
            )
            
            #    ()
            if related_object:
                if hasattr(related_object, 'project') and hasattr(related_object.project, 'id'):
                    notification.project_id = related_object.project.id
                elif hasattr(related_object, 'id') and hasattr(related_object, '_meta') and hasattr(related_object, '_meta') and related_object._meta.model_name == 'project':
                    notification.project_id = related_object.id
            
            notification.save()
            
            logger.info(f"  : {user.email} - {notification_type}")
            return notification
            
        except Exception as e:
            logger.error(f"   : {str(e)}")
            return None
    
    @staticmethod
    def notify_invitation_received(invitation):
        """  """
        try:
            #       
            invitee_user = User.objects.filter(email=invitation.invitee_email).first()
            if not invitee_user:
                return None
            
            title = f"'{invitation.project.name}'  "
            message = f"{invitation.inviter.nickname}  ."
            action_url = f"/invitation/{invitation.token}"
            
            return NotificationService.create_notification(
                user=invitee_user,
                notification_type='INVITATION_RECEIVED',
                title=title,
                message=message,
                related_object=invitation,
                action_url=action_url
            )
            
        except Exception as e:
            logger.error(f"     : {str(e)}")
            return None
    
    @staticmethod
    def notify_invitation_accepted(invitation):
        """   ()"""
        try:
            title = f" "
            message = f"{invitation.invitee_email} '{invitation.project.name}'   ."
            action_url = f"/project/{invitation.project.id}"
            
            return NotificationService.create_notification(
                user=invitation.inviter,
                notification_type='INVITATION_ACCEPTED',
                title=title,
                message=message,
                related_object=invitation,
                action_url=action_url
            )
            
        except Exception as e:
            logger.error(f"     : {str(e)}")
            return None
    
    @staticmethod
    def notify_invitation_declined(invitation):
        """   ()"""
        try:
            title = f" "
            message = f"{invitation.invitee_email} '{invitation.project.name}'   ."
            action_url = f"/project/{invitation.project.id}"
            
            return NotificationService.create_notification(
                user=invitation.inviter,
                notification_type='INVITATION_DECLINED',
                title=title,
                message=message,
                related_object=invitation,
                action_url=action_url
            )
            
        except Exception as e:
            logger.error(f"     : {str(e)}")
            return None
    
    @staticmethod
    def notify_member_joined(project, new_member):
        """    ( )"""
        try:
            #    ( + )
            project_members = []
            
            #  
            if project.user:
                project_members.append(project.user)
            
            #   
            existing_members = models.Members.objects.filter(project=project).select_related('user')
            for member in existing_members:
                if member.user not in project_members:
                    project_members.append(member.user)
            
            #    
            project_members = [member for member in project_members if member != new_member]
            
            title = f"  "
            message = f"{new_member.nickname} '{project.name}'  ."
            action_url = f"/project/{project.id}"
            
            notifications = []
            for member in project_members:
                notification = NotificationService.create_notification(
                    user=member,
                    notification_type='MEMBER_JOINED',
                    title=title,
                    message=message,
                    related_object=project,
                    action_url=action_url
                )
                if notification:
                    notifications.append(notification)
            
            return notifications
            
        except Exception as e:
            logger.error(f"      : {str(e)}")
            return []
    
    @staticmethod
    def get_user_notifications(user, unread_only=False, limit=20):
        """  """
        try:
            queryset = Notification.objects.filter(recipient=user)
            
            if unread_only:
                queryset = queryset.filter(is_read=False)
            
            return queryset.order_by('-created')[:limit]
            
        except Exception as e:
            logger.error(f"    : {str(e)}")
            return []
    
    @staticmethod
    def mark_as_read(notification_ids, user):
        """  """
        try:
            updated_count = Notification.objects.filter(
                id__in=notification_ids,
                recipient=user
            ).update(is_read=True)
            
            logger.info(f"  : {updated_count}")
            return updated_count
            
        except Exception as e:
            logger.error(f"    : {str(e)}")
            return 0
    
    @staticmethod
    def get_unread_count(user):
        """   """
        try:
            return Notification.objects.filter(recipient=user, is_read=False).count()
        except Exception as e:
            logger.error(f"      : {str(e)}")
            return 0