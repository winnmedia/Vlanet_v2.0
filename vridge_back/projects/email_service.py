"""
    
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
import logging
from users.email_queue import email_queue_manager

logger = logging.getLogger(__name__)

class ProjectInvitationEmailService:
    """   """
    
    @staticmethod
    def send_invitation_email(invitation):
        """   """
        try:
            #   
            invitation_url = f"{settings.FRONTEND_URL}/invitation/{invitation.token}"
            
            #  
            subject = f"[VideoPlanet] {invitation.project.name}  "
            
            #   (HTML) -   
            html_message = render_to_string('emails/project_invitation_premium.html', {
                'project_name': invitation.project.name,
                'inviter_name': invitation.inviter.nickname,
                'invitation_url': invitation_url,
                'message': invitation.message,
                'site_name': 'VideoPlanet',
                'site_url': settings.FRONTEND_URL,
            })
            
            #   ()
            text_message = f"""
!

{invitation.inviter.nickname} "{invitation.project.name}"  .

 : {invitation.message}

    :
{invitation_url}

  {invitation.expires_at.strftime('%Y %m %d')} .

.
VideoPlanet 
            """
            
            #    ( )
            email_id = email_queue_manager.add_email(
                subject=subject,
                body=text_message,
                recipient_list=[invitation.invitee_email],
                html_message=html_message,
                priority=2,  #  
                email_type='invitation'
            )
            
            if email_id:
                logger.info(f"   : {invitation.invitee_email} (ID: {email_id})")
                return True
            else:
                logger.error(f"    : {invitation.invitee_email}")
                return False
                
        except Exception as e:
            logger.error(f"    : {str(e)}")
            return False
    
    @staticmethod
    def send_invitation_accepted_email(invitation):
        """    ()"""
        try:
            subject = f"[VideoPlanet] {invitation.invitee_email}  "
            
            html_message = render_to_string('emails/invitation_accepted_premium.html', {
                'project_name': invitation.project.name,
                'project_id': invitation.project.id,
                'invitee_name': invitation.invitee_email.split('@')[0],
                'site_name': 'VideoPlanet',
                'site_url': settings.FRONTEND_URL,
            })
            
            text_message = f"""
 {invitation.inviter.nickname}!

{invitation.invitee_email} "{invitation.project.name}"   .

     .

.
VideoPlanet 
            """
            
            email_id = email_queue_manager.add_email(
                subject=subject,
                body=text_message,
                recipient_list=[invitation.inviter.email],
                html_message=html_message,
                priority=3,  #  
                email_type='notification'
            )
            
            if email_id:
                logger.info(f"    : {invitation.inviter.email} (ID: {email_id})")
                return True
            else:
                logger.error(f"     : {invitation.inviter.email}")
                return False
                
        except Exception as e:
            logger.error(f"      : {str(e)}")
            return False
    
    @staticmethod
    def send_invitation_declined_email(invitation):
        """    ()"""
        try:
            subject = f"[VideoPlanet] {invitation.invitee_email}  "
            
            html_message = render_to_string('emails/invitation_declined_premium.html', {
                'project_name': invitation.project.name,
                'project_id': invitation.project.id,
                'invitee_name': invitation.invitee_email.split('@')[0],
                'site_name': 'VideoPlanet',
                'site_url': settings.FRONTEND_URL,
            })
            
            text_message = f"""
 {invitation.inviter.nickname}!

{invitation.invitee_email} "{invitation.project.name}"   .

      .

.
VideoPlanet 
            """
            
            email_id = email_queue_manager.add_email(
                subject=subject,
                body=text_message,
                recipient_list=[invitation.inviter.email],
                html_message=html_message,
                priority=3,  #  
                email_type='notification'
            )
            
            if email_id:
                logger.info(f"    : {invitation.inviter.email} (ID: {email_id})")
                return True
            else:
                logger.error(f"     : {invitation.inviter.email}")
                return False
                
        except Exception as e:
            logger.error(f"      : {str(e)}")
            return False