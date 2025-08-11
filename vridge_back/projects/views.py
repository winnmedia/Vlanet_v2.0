import logging, json, random
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)
from datetime import datetime, timedelta
from django.shortcuts import render
from django.utils import timezone
from django.utils import timezone as django_timezone
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
import secrets
from users.utils import (
    user_validator,
    project_token_generator,
    check_project_token,
)
from . import models
from feedbacks import models as feedback_model
from .utils_date import parse_date_flexible
from common.exceptions import APIException
from core.response_handler import StandardResponse
from core.error_messages import ErrorMessages
# from .views_feedback import ProjectFeedback, ProjectFeedbackComments, ProjectFeedbackUpload

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

from django.db.models import F, Case, When, Value, Subquery, OuterRef, Count
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone as django_timezone
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings
import os
import secrets
import hashlib
from datetime import timedelta
from django.utils import timezone


@method_decorator(csrf_exempt, name='dispatch')
class ProjectList(View):
    @user_validator
    def get(self, request):
        try:
            logger.info(f"ProjectList GET request from user: {request.user.email}")
            user = request.user
            
            #   (  - django_cache_table )
            # cache_key = f"project_list_{user.id}"
            # cached_result = cache.get(cache_key)
            # 
            # if cached_result is not None:
            #     logger.info(f"Returning cached project list for user: {user.email}")
            #     return JsonResponse(cached_result, safe=False)
            
            # nickname 
            if user.nickname:
                nickname = user.nickname
            else:
                nickname = user.username

            # development_framework    
            # : feedbacks__comments__user  N+1  
            project_list = user.projects.all().select_related(
                "basic_plan",
                "story_board",
                "filming",
                "video_edit",
                "post_work",
                "video_preview",
                "confirmation",
                "video_delivery"
            ).prefetch_related(
                'feedbacks',  #    
                'feedbacks__comments__user',  #      
                'members__user',  #     
                'invitations'  #    
            )
            result = []
            for i in project_list:
                if i.video_delivery and i.video_delivery.end_date:
                    end_date = i.video_delivery.end_date
                elif i.confirmation and i.confirmation.end_date:
                    end_date = i.confirmation.end_date
                elif i.video_preview and i.video_preview.end_date:
                    end_date = i.video_preview.end_date
                elif i.post_work and i.post_work.end_date:
                    end_date = i.post_work.end_date
                elif i.video_edit and i.video_edit.end_date:
                    end_date = i.video_edit.end_date
                elif i.filming and i.filming.end_date:
                    end_date = i.filming.end_date
                elif i.story_board and i.story_board.end_date:
                    end_date = i.story_board.end_date
                elif i.basic_plan and i.basic_plan.end_date:
                    end_date = i.basic_plan.end_date
                else:
                    end_date = None

                if i.basic_plan and i.basic_plan.start_date:
                    first_date = i.basic_plan.start_date
                elif i.story_board and i.story_board.start_date:
                    first_date = i.story_board.start_date
                elif i.filming and i.filming.start_date:
                    first_date = i.filming.start_date
                elif i.video_edit and i.video_edit.start_date:
                    first_date = i.video_edit.start_date
                elif i.post_work and i.post_work.start_date:
                    first_date = i.post_work.start_date
                elif i.video_preview and i.video_preview.start_date:
                    first_date = i.video_preview.start_date
                elif i.confirmation and i.confirmation.start_date:
                    first_date = i.confirmation.start_date
                elif i.video_delivery and i.video_delivery.start_date:
                    first_date = i.video_delivery.start_date
                else:
                    first_date = None

                result.append(
                    {
                        "id": i.id,
                        "name": i.name,
                        "manager": i.manager,
                        "consumer": i.consumer,
                        "description": i.description,
                        "color": i.color,
                        "basic_plan": {
                            "start_date": i.basic_plan.start_date if i.basic_plan else None,
                            "end_date": i.basic_plan.end_date if i.basic_plan else None,
                        },
                        "story_board": {
                            "start_date": i.story_board.start_date if i.story_board else None,
                            "end_date": i.story_board.end_date if i.story_board else None,
                        },
                        "filming": {
                            "start_date": i.filming.start_date if i.filming else None,
                            "end_date": i.filming.end_date if i.filming else None,
                        },
                        "video_edit": {
                            "start_date": i.video_edit.start_date if i.video_edit else None,
                            "end_date": i.video_edit.end_date if i.video_edit else None,
                        },
                        "post_work": {
                            "start_date": i.post_work.start_date if i.post_work else None,
                            "end_date": i.post_work.end_date if i.post_work else None,
                        },
                        "video_preview": {
                            "start_date": i.video_preview.start_date if i.video_preview else None,
                            "end_date": i.video_preview.end_date if i.video_preview else None,
                        },
                        "confirmation": {
                            "start_date": i.confirmation.start_date if i.confirmation else None,
                            "end_date": i.confirmation.end_date if i.confirmation else None,
                        },
                        "video_delivery": {
                            "start_date": i.video_delivery.start_date if i.video_delivery else None,
                            "end_date": i.video_delivery.end_date if i.video_delivery else None,
                        },
                        "first_date": first_date,
                        "end_date": end_date,
                        "created": i.created,
                        "updated": i.updated,
                        "owner_nickname": i.user.nickname,
                        "owner_email": i.user.username,
                        "feedback_id": i.feedback.id if i.feedback else None,
                        "feedback": [
                            {
                                "id": fb.id,
                                "text": fb.text,
                                "nickname": fb.user.nickname if not fb.security else "",
                                "section": fb.section,
                                "title": fb.title,
                                "created": fb.created,
                                "updated": fb.updated,
                            }
                            for fb in (i.feedback.comments.all() if i.feedback else [])
                        ],
                        # "pending_list": list(i.invites.all().values("id", "email")),
                        "member_list": list(
                            i.members.all()
                            .annotate(email=F("user__username"), nickname=F("user__nickname"))
                            .values("id", "rating", "email", "nickname")
                        ),
                        # "files": list(i.files.all().values("id", "files")),
                    }
                )

            members = user.members.all().select_related(
                "project", 
                "project__basic_plan",
                "project__story_board",
                "project__filming",
                "project__video_edit",
                "project__post_work",
                "project__video_preview",
                "project__confirmation",
                "project__video_delivery",
                "project__user"
            ).prefetch_related(
                'project__feedbacks',
                'project__feedbacks__comments'
            )
            for i in members:
                if i.project.video_delivery and i.project.video_delivery.end_date:
                    end_date = i.project.video_delivery.end_date
                elif i.project.confirmation and i.project.confirmation.end_date:
                    end_date = i.project.confirmation.end_date
                elif i.project.video_preview and i.project.video_preview.end_date:
                    end_date = i.project.video_preview.end_date
                elif i.project.post_work and i.project.post_work.end_date:
                    end_date = i.project.post_work.end_date
                elif i.project.video_edit and i.project.video_edit.end_date:
                    end_date = i.project.video_edit.end_date
                elif i.project.filming and i.project.filming.end_date:
                    end_date = i.project.filming.end_date
                elif i.project.story_board and i.project.story_board.end_date:
                    end_date = i.project.story_board.end_date
                elif i.project.basic_plan and i.project.basic_plan.end_date:
                    end_date = i.project.basic_plan.end_date
                else:
                    end_date = None

                if i.project.basic_plan and i.project.basic_plan.start_date:
                    first_date = i.project.basic_plan.start_date
                elif i.project.story_board and i.project.story_board.start_date:
                    first_date = i.project.story_board.start_date
                elif i.project.filming and i.project.filming.start_date:
                    first_date = i.project.filming.start_date
                elif i.project.video_edit and i.project.video_edit.start_date:
                    first_date = i.project.video_edit.start_date
                elif i.project.post_work and i.project.post_work.start_date:
                    first_date = i.project.post_work.start_date
                elif i.project.video_preview and i.project.video_preview.start_date:
                    first_date = i.project.video_preview.start_date
                elif i.project.confirmation and i.project.confirmation.start_date:
                    first_date = i.project.confirmation.start_date
                elif i.project.video_delivery and i.project.video_delivery.start_date:
                    first_date = i.project.video_delivery.start_date
                else:
                    first_date = None
                result.append(
                    {
                        "id": i.project.id,
                        "name": i.project.name,
                        "manager": i.project.manager,
                        "consumer": i.project.consumer,
                        "description": i.project.description,
                        "color": i.project.color,
                        "basic_plan": {
                            "start_date": i.project.basic_plan.start_date if i.project.basic_plan else None,
                            "end_date": i.project.basic_plan.end_date if i.project.basic_plan else None,
                        },
                        "story_board": {
                            "start_date": i.project.story_board.start_date if i.project.story_board else None,
                            "end_date": i.project.story_board.end_date if i.project.story_board else None,
                        },
                        "filming": {
                            "start_date": i.project.filming.start_date if i.project.filming else None,
                            "end_date": i.project.filming.end_date if i.project.filming else None,
                        },
                        "video_edit": {
                            "start_date": i.project.video_edit.start_date if i.project.video_edit else None,
                            "end_date": i.project.video_edit.end_date if i.project.video_edit else None,
                        },
                        "post_work": {
                            "start_date": i.project.post_work.start_date if i.project.post_work else None,
                            "end_date": i.project.post_work.end_date if i.project.post_work else None,
                        },
                        "video_preview": {
                            "start_date": i.project.video_preview.start_date if i.project.video_preview else None,
                            "end_date": i.project.video_preview.end_date if i.project.video_preview else None,
                        },
                        "confirmation": {
                            "start_date": i.project.confirmation.start_date if i.project.confirmation else None,
                            "end_date": i.project.confirmation.end_date if i.project.confirmation else None,
                        },
                        "video_delivery": {
                            "start_date": i.project.video_delivery.start_date if i.project.video_delivery else None,
                            "end_date": i.project.video_delivery.end_date if i.project.video_delivery else None,
                        },
                        "first_date": first_date,
                        "end_date": end_date,
                        "created": i.project.created,
                        "updated": i.project.updated,
                        "owner_nickname": i.project.user.nickname,
                        "owner_email": i.project.user.username,
                        "feedback_id": i.project.feedback.id if i.project.feedback else None,
                        "feedback": [
                            {
                                "id": fb.id,
                                "text": fb.text,
                                "nickname": fb.user.nickname if not fb.security else "",
                                "section": fb.section,
                                "title": fb.title,
                                "created": fb.created,
                                "updated": fb.updated,
                            }
                            for fb in (i.project.feedback.comments.all() if i.project.feedback else [])
                        ],
                        # "pending_list": list(i.project.invites.all().values("id", "email")),
                        "member_list": list(
                            i.project.members.all()
                            .annotate(email=F("user__username"), nickname=F("user__nickname"))
                            .values("id", "rating", "email", "nickname")
                        ),
                        # "files": list(i.project.files.all().values("id", "files")),
                    }
                )

            sample_files = [
                {
                    "file_name": i.files.name,
                    "files": "http://127.0.0.1:8000" + i.files.url if settings.DEBUG else i.files.url,
                }
                for i in models.SampleFiles.objects.all()
                if i.files
            ]

            # user_memos  
            try:
                user_memos = list(user.memos.all().values("id", "date", "memo"))
            except AttributeError:
                user_memos = []
            
            #   URL 
            profile_image = None
            try:
                if hasattr(user, 'profile') and user.profile.profile_image:
                    profile_image = user.profile.profile_image.url
            except:
                pass

            #   
            response_data = {
                "result": result,
                "user": user.username,
                "nickname": nickname,
                "profile_image": profile_image,
                "sample_files": sample_files,
                "user_memos": user_memos,
            }
            
            #   (5 ) -  
            # cache.set(cache_key, response_data, 300)
            # logger.info(f"Cached project list for user: {user.email}")
            
            return JsonResponse(response_data, status=200)
        except Exception as e:
            logger.error(f"Error in ProjectList: {str(e)}", exc_info=True)
            logging.error(f"ProjectList error for user {request.user.id}: {str(e)}")
            import traceback
            logging.error(f"Traceback: {traceback.format_exc()}")
            
            #     
            error_message = "     ."
            error_detail = str(e)
            
            # development_framework   
            if "development_framework" in error_detail or "column" in error_detail:
                error_message = "   .    ."
                logger.error("Development framework column missing - migration needed")
            elif "nickname" in error_detail:
                error_message = "   ."
            elif "memos" in error_detail:
                error_message = "     ."
                
            return JsonResponse({
                "message": error_message,
                "error": error_detail[:200] if settings.DEBUG else None  #    
            }, status=500)


#   ,   ,   
@method_decorator(csrf_exempt, name='dispatch')
class InviteMember(View):
    @user_validator
    def post(self, request, project_id):
        try:
            user = request.user

            data = json.loads(request.body)
            email = data.get("email")

            try:
                project = models.Project.objects.get(id=project_id)
            except models.Project.DoesNotExist:
                return JsonResponse({"message": "  ."}, status=404)

            if project.user.username == email:
                return JsonResponse({"message": "   ."}, status=400)

            members = project.members.all().filter(user__username=email)
            if members.exists():
                return JsonResponse({"message": "  ."}, status=409)

            #    
            invitation = None
            resend = False
            use_legacy = False
            
            # ProjectInvitation       
            try:
                #    ( )
                existing_invitation = models.ProjectInvitation.objects.filter(
                    project=project,
                    invitee_email=email,
                    status='pending'
                ).first()
                
                if existing_invitation:
                    #   
                    if data.get('resend'):
                        invitation = existing_invitation
                        resend = True
                    else:
                        return JsonResponse({"message": "    .    ."}, status=409)
                else:
                    #   
                    with transaction.atomic():
                        import secrets
                        token = secrets.token_urlsafe(32)
                        invitation = models.ProjectInvitation.objects.create(
                            project=project,
                            inviter=user,
                            invitee_email=email,
                            message=data.get('message', ''),
                            token=token,
                            expires_at=timezone.now() + timedelta(days=7)
                        )
                        resend = False
            except Exception as db_error:
                logger.error(f"ProjectInvitation  : {str(db_error)}")
                #    (ProjectInvite)
                use_legacy = True
                existing_invite = models.ProjectInvite.objects.filter(
                    project=project,
                    email=email
                ).first()
                
                if existing_invite and not data.get('resend'):
                    return JsonResponse({"message": "    ."}, status=409)
                
                #    
                if not existing_invite:
                    with transaction.atomic():
                        models.ProjectInvite.objects.create(
                            project=project,
                            email=email
                        )
            
            #       
            if use_legacy:
                return JsonResponse({
                    "message": " .",
                    "email_sent": False,
                    "resent": data.get('resend', False),
                    "invitation_id": None,
                    "invitation_url": None
                }, status=200)
            
            #    -    
            email_sent = False
            invitation_id = None
            invitation_url = None
            invitation_object = None
            
            #    ( )
            if 'invitation' in locals() and invitation:
                invitation_object = invitation
                invitation_url = f"{settings.FRONTEND_URL}/invitation/{invitation.token}"
                invitation_id = invitation.id
            
            #   
            if invitation_object:
                logger.info(f"[InviteMember] Attempting to send email to {email} for project {project.name}")
                try:
                    from django.core.mail import send_mail
                    
                    #  
                    subject = f"[VideoPlanet] {project.name}  "
                    
                    #   
                    expires_date = invitation_object.expires_at.strftime('%Y %m %d')
                    
                    #  
                    message = f"""
!

{user.nickname or user.username} "{project.name}"  .

 : {data.get('message', '')}

    :
{invitation_url}

  {expires_date} .

.
VideoPlanet 
                    """
                    
                    # HTML  
                    html_message = f"""
                    <html>
                    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                            <h2 style="color: #1631F8;">VideoPlanet  </h2>
                            <p>!</p>
                            <p><strong>{user.nickname or user.username}</strong> "<strong>{project.name}</strong>"  .</p>
                            
                            {f'<p><strong> :</strong> {data.get("message", "")}</p>' if data.get("message") else ''}
                            
                            <div style="margin: 30px 0; text-align: center;">
                                <a href="{invitation_url}" 
                                   style="display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, #1631F8 0%, #0F23C9 100%); 
                                          color: white; text-decoration: none; border-radius: 8px; font-weight: bold;">
                                     
                                </a>
                            </div>
                            
                            <p style="color: #666; font-size: 14px;">
                                       :<br>
                                <span style="word-break: break-all; color: #1631F8;">{invitation_url}</span>
                            </p>
                            
                            <p style="color: #666; font-size: 14px;">
                                  <strong>{expires_date}</strong> .
                            </p>
                            
                            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                            
                            <p style="color: #999; font-size: 12px; text-align: center;">
                                VideoPlanet -     <br>
                                <a href="https://vlanet.net" style="color: #1631F8;">vlanet.net</a>
                            </p>
                        </div>
                    </body>
                    </html>
                    """
                    
                    #   (HTML  )
                    from django.core.mail import EmailMultiAlternatives
                    
                    email_message = EmailMultiAlternatives(
                        subject=subject,
                        body=message,  #  
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[email]
                    )
                    email_message.attach_alternative(html_message, "text/html")
                    
                    # SendGrid   
                    email_message.extra_headers = {
                        'X-SMTPAPI': '{"filters": {"clicktrack": {"settings": {"enable": 0}}}}'
                    }
                    
                    email_sent = email_message.send(fail_silently=False)
                    logger.info(f"[InviteMember] Email send result: {email_sent}")
                except Exception as e:
                    logger.error(f"[InviteMember] Email send error: {str(e)}")
                    #      
                    email_sent = False
            
            #     -  
            try:
                from users.models import RecentInvitation
                recent_invite, created = RecentInvitation.objects.get_or_create(
                    inviter=user,
                    invitee_email=email,
                    defaults={
                        'invitee_name': email.split('@')[0],  #  username   
                        'project_name': project.name,
                        'invitation_count': 1
                    }
                )
                if not created:
                    recent_invite.project_name = project.name
                    recent_invite.invitation_count += 1
                    recent_invite.save()
            except Exception as e:
                logger.warning(f"    : {str(e)}")
                # RecentInvitation      
            
            #       
            # resend    
            is_resend = False
            if 'resend' in locals():
                is_resend = resend
            else:
                is_resend = data.get('resend', False)
            
            return JsonResponse({
                "message": " ." if not is_resend else " .",
                "email_sent": email_sent,
                "resent": is_resend,
                "invitation_id": invitation_id,
                "invitation_url": invitation_url
            }, status=200)
        except Exception as e:
            logger.error(f"Error in InviteMember: {str(e)}", exc_info=True)
            
            #    
            if "token" in str(e):
                return JsonResponse({"message": "     ."}, status=500)
            elif "email" in str(e):
                return JsonResponse({"message": "    ."}, status=500)
            elif "database" in str(e) or "relation" in str(e):
                return JsonResponse({"message": "  ."}, status=500)
            else:
                return JsonResponse({"message": f"    : {str(e)}"}, status=500)

    @user_validator
    def delete(self, request, project_id):
        try:
            user = request.user
            data = json.loads(request.body)
            pk = data.get("pk")

            project = models.Project.objects.get_or_none(id=project_id)
            if project is None:
                return JsonResponse({"message": "    ."}, status=404)

            is_member = models.Members.objects.get_or_none(project=project, user=user, rating="manager")
            if project.user != user and is_member is None:
                return StandardResponse.forbidden()

            invite = models.ProjectInvite.objects.get_or_none(pk=pk)
            if invite:
                invite.delete()
            return StandardResponse.success(message="")
        except Exception as e:
            logger.error(f"Error in project operation: {str(e)}", exc_info=True)
            logging.info(str(e))
            return StandardResponse.server_error()


#        ,   
#      
@method_decorator(csrf_exempt, name='dispatch')
class LegacyInviteRedirect(View):
    """     """
    def get(self, request, uid, token):
        """    -   """
        return JsonResponse({
            "status": "error",
            "message": "      .   .",
            "redirect_url": f"{settings.FRONTEND_URL}/CmsHome"
        }, status=410)  # 410 Gone -     

@method_decorator(csrf_exempt, name='dispatch')
class AcceptInvite(View):
    @user_validator
    def get(self, request, uid, token):
        try:
            logger.info(f"[AcceptInvite] Request received - uid: {uid}, token: {token}")
            user = request.user
            logger.info(f"[AcceptInvite] User: {user.username}")
            
            try:
                project_id = force_str(urlsafe_base64_decode(uid))
                logger.info(f"[AcceptInvite] Decoded project_id: {project_id}")
            except Exception as decode_error:
                logger.error(f"[AcceptInvite] Error decoding uid: {decode_error}")
                return JsonResponse({"message": "  ."}, status=400)

            project = models.Project.objects.get_or_none(id=project_id)
            logger.info(f"[AcceptInvite] Project found: {project is not None}")
            
            if not project:
                logger.error(f"[AcceptInvite] Project not found with id: {project_id}")
                return JsonResponse({"message": "  ."}, status=404)
            
            is_member = project.members.filter(user=user)
            logger.info(f"[AcceptInvite] User is already member: {is_member.exists()}")
            
            if is_member.exists():
                logger.info(f"[AcceptInvite] User is already a member of project {project.name}")
                return JsonResponse({"message": "  ."}, status=400)
            
            if project.user == user:
                logger.info(f"[AcceptInvite] User is project owner")
                return JsonResponse({"message": " ."}, status=400)

            invite_obj = models.ProjectInvite.objects.get_or_none(project=project, email=user.username)
            if invite_obj is None:
                return JsonResponse({"message": " ."}, status=400)

            if not check_project_token(project, token):
                return JsonResponse({"message": " ."}, status=400)

            models.Members.objects.create(project=project, user=user)
            invite_obj.delete()

            return StandardResponse.success(message="")
        except Exception as e:
            logger.error(f"Error in project operation: {str(e)}", exc_info=True)
            logging.info(str(e))
            return StandardResponse.server_error()


@method_decorator(csrf_exempt, name='dispatch')
class CreateProject(View):
    @user_validator
    def post(self, request):
        try:
            user = request.user
            files = request.FILES.getlist("files")
            
            # Content-Type   
            if request.content_type == 'application/json':
                # JSON  
                try:
                    data = json.loads(request.body)
                    inputs = {
                        'name': data.get('name'),
                        'manager': data.get('manager'),
                        'consumer': data.get('consumer'),
                        'description': data.get('description'),
                        'color': data.get('color', '#1631F8')
                    }
                    process = data.get('process', [])
                except json.JSONDecodeError:
                    return JsonResponse({
                        "message": " JSON .",
                        "code": "INVALID_JSON"
                    }, status=400)
            else:
                # FormData   ( )
                inputs_raw = request.POST.get("inputs")
                process_raw = request.POST.get("process")
                
                if not inputs_raw or not process_raw:
                    return JsonResponse({
                        "message": "    :   .",
                        "code": "MISSING_DATA"
                    }, status=400)
                
                try:
                    inputs = json.loads(inputs_raw)
                    process = json.loads(process_raw)
                except json.JSONDecodeError as e:
                    return JsonResponse({
                        "message": f"    :   .",
                        "code": "INVALID_JSON"
                    }, status=400)
            
            # inputs process 
            if not inputs or process is None:
                return JsonResponse({
                    "message": "    :   .",
                    "code": "MISSING_DATA"
                }, status=400)
            
            # inputs dict  (string    )
            if isinstance(inputs, str):
                try:
                    inputs = json.loads(inputs)
                except json.JSONDecodeError:
                    return JsonResponse({
                        "message": "    : inputs    .",
                        "code": "INVALID_INPUTS_FORMAT"
                    }, status=400)
            
            if isinstance(process, str):
                try:
                    process = json.loads(process)
                except json.JSONDecodeError:
                    return JsonResponse({
                        "message": "    : process    .",
                        "code": "INVALID_PROCESS_FORMAT"
                    }, status=400)
            
            #   
            idempotency_key = request.headers.get('X-Idempotency-Key')
            if idempotency_key:
                logging.info(f"[CreateProject] Request with idempotency key: {idempotency_key}")
                
                #     (Django  )
                from django.core.cache import cache
                cache_key = f"create_project_{user.id}_{idempotency_key}"
                
                #    
                cached_result = cache.get(cache_key)
                if cached_result:
                    logging.info(f"[CreateProject] Returning cached result for idempotency key: {idempotency_key}")
                    return JsonResponse(cached_result, status=200)
            
            #     (   )
            project_name = inputs.get('name')
            if project_name:
                #      
                existing_project = models.Project.objects.filter(
                    user=user,
                    name=project_name
                ).exists()
                
                if existing_project:
                    logging.warning(f"[CreateProject] Duplicate project creation attempt: {project_name}")
                    return JsonResponse({
                        "message": "    .",
                        "code": "DUPLICATE_PROJECT_NAME"
                    }, status=400)

            with transaction.atomic():
                #       
                #       
                # is_public  
                project = models.Project(
                    user=user,
                    name=inputs.get('name'),
                    manager=inputs.get('manager'),
                    consumer=inputs.get('consumer'),
                    description=inputs.get('description', ''),
                    color=inputs.get('color', '#1631F8')
                )
                
                #   (  )
                if 'tone_manner' in inputs:
                    project.tone_manner = inputs['tone_manner']
                if 'genre' in inputs:
                    project.genre = inputs['genre']
                if 'concept' in inputs:
                    project.concept = inputs['concept']
                
                #    Railway    
                # try:
                #     if hasattr(project, 'is_public'):
                #         project.is_public = False  # 
                # except Exception:
                #     pass
                
                project.save()
                
                logging.info(f"[CreateProject] Creating project '{project_name}' for user {user.username}")
                logging.info(f"[CreateProject] Inputs: {inputs}")
                logging.info(f"[CreateProject] Process data: {process}")

                for i in process:
                    key = i.get("key")
                    start_date = i.get("startDate")
                    end_date = i.get("endDate")
                    
                    #   datetime   ( )
                    try:
                        start_date = parse_date_flexible(start_date)
                        end_date = parse_date_flexible(end_date)
                    except ValueError as e:
                        logging.error(f"Date parsing error for {key}: {str(e)}")
                        logging.error(f"Start date: {start_date}, End date: {end_date}")
                        return JsonResponse({
                            "message": f"{key}     .",
                            "error": str(e)
                        }, status=400)
                    
                    if key == "basic_plan":
                        basic_plan = models.BasicPlan.objects.create(start_date=start_date, end_date=end_date)
                        setattr(project, key, basic_plan)
                    elif key == "story_board":
                        story_board = models.Storyboard.objects.create(
                            start_date=start_date, end_date=end_date
                        )
                        setattr(project, key, story_board)
                    elif key == "filming":
                        filming = models.Filming.objects.create(start_date=start_date, end_date=end_date)
                        setattr(project, key, filming)
                    elif key == "video_edit":
                        video_edit = models.VideoEdit.objects.create(start_date=start_date, end_date=end_date)
                        setattr(project, key, video_edit)
                    elif key == "post_work":
                        post_work = models.PostWork.objects.create(start_date=start_date, end_date=end_date)
                        setattr(project, key, post_work)
                    elif key == "video_preview":
                        video_preview = models.VideoPreview.objects.create(
                            start_date=start_date, end_date=end_date
                        )
                        setattr(project, key, video_preview)
                    elif key == "confirmation":
                        confirmation = models.Confirmation.objects.create(
                            start_date=start_date, end_date=end_date
                        )
                        setattr(project, key, confirmation)
                    elif key == "video_delivery":
                        video_delivery = models.VideoDelivery.objects.create(
                            start_date=start_date, end_date=end_date
                        )
                        setattr(project, key, video_delivery)

                # FeedBack  -    
                # Project   ForeignKey   
                #   
                project.color = "".join(
                    ["#" + "".join([random.choice("0123456789ABCDEF") for j in range(6)])]
                )
                project.save()
                
                #    FeedBack  (ForeignKey )
                feedback = feedback_model.FeedBack.objects.create(
                    project=project,
                    user=user,
                    title=f"{project.name} ",
                    status='open'
                )
                logging.info(f"[CreateProject] Created feedback for project {project.id}")

                file_obj = []
                for f in files:
                    file_obj.append(models.File(project=project, files=f))

                models.File.objects.bulk_create(file_obj)

            #    
            result = {
                "message": "success", 
                "project_id": project.id,
                "project_name": project.name
            }
            if idempotency_key:
                from django.core.cache import cache
                cache_key = f"create_project_{user.id}_{idempotency_key}"
                # 5  
                # cache.set(cache_key, result, 300)  #  
            
            logging.info(f"[CreateProject] Successfully created project '{project_name}' with ID: {project.id}")
            return JsonResponse(result, status=200)
        except Exception as e:
            logger.error(f"Error in project operation: {str(e)}", exc_info=True)
            logging.error(f"Project creation error: {str(e)}")
            logging.error(f"Error type: {type(e).__name__}")
            import traceback
            logging.error(f"Traceback: {traceback.format_exc()}")
            
            #     
            if "key" in str(e):
                return JsonResponse({"message": "    .     ."}, status=400)
            elif "date" in str(e).lower():
                return JsonResponse({"message": "   ."}, status=400)
            else:
                return JsonResponse({"message": f"    : {str(e)}"}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ProjectDetail(View):
    @user_validator
    def get(self, request, project_id):
        try:
            user = request.user
            
            #   ( )
            # cache_key = f"project_detail_{project_id}_{user.id}"
            # cached_result = cache.get(cache_key)
            # 
            # if cached_result is not None:
            #     logger.info(f"Returning cached project detail for project: {project_id}, user: {user.email}")
            #     return JsonResponse({"result": cached_result}, status=200)
            
            try:
                #  :      
                project = models.Project.objects.select_related(
                    'user',
                    'basic_plan',
                    'story_board',
                    'filming',
                    'video_edit',
                    'post_work',
                    'video_preview',
                    'confirmation',
                    'video_delivery'
                ).prefetch_related(
                    'feedbacks',
                    'members__user',
                    'files',
                    'memos',
                    'invitations'
                ).get(id=project_id)
            except models.Project.DoesNotExist:
                return StandardResponse.not_found("")

            is_member = project.members.filter(user=user).exists()
            if project.user != user and not is_member:
                return StandardResponse.forbidden()

            result = {
                "id": project.id,
                "name": project.name,
                "manager": project.manager,
                "consumer": project.consumer,
                "description": project.description,
                "color": project.color,
                "basic_plan": {
                    "key": "basic_plan",
                    "start_date": project.basic_plan.start_date if project.basic_plan else None,
                    "end_date": project.basic_plan.end_date if project.basic_plan else None,
                },
                "story_board": {
                    "key": "story_board",
                    "start_date": project.story_board.start_date if project.story_board else None,
                    "end_date": project.story_board.end_date if project.story_board else None,
                },
                "filming": {
                    "key": "filming",
                    "start_date": project.filming.start_date if project.filming else None,
                    "end_date": project.filming.end_date if project.filming else None,
                },
                "video_edit": {
                    "key": "video_edit",
                    "start_date": project.video_edit.start_date if project.video_edit else None,
                    "end_date": project.video_edit.end_date if project.video_edit else None,
                },
                "post_work": {
                    "key": "post_work",
                    "start_date": project.post_work.start_date if project.post_work else None,
                    "end_date": project.post_work.end_date if project.post_work else None,
                },
                "video_preview": {
                    "key": "video_preview",
                    "start_date": project.video_preview.start_date if project.video_preview else None,
                    "end_date": project.video_preview.end_date if project.video_preview else None,
                },
                "confirmation": {
                    "key": "confirmation",
                    "start_date": project.confirmation.start_date if project.confirmation else None,
                    "end_date": project.confirmation.end_date if project.confirmation else None,
                },
                "video_delivery": {
                    "key": "video_delivery",
                    "start_date": project.video_delivery.start_date if project.video_delivery else None,
                    "end_date": project.video_delivery.end_date if project.video_delivery else None,
                },
                "owner_nickname": project.user.nickname,
                "owner_email": project.user.username,
                "created": project.created,
                "updated": project.updated,
                "pending_list": [],  #   -     
                "member_list": list(
                    project.members.all()
                    .annotate(email=F("user__username"), nickname=F("user__nickname"))
                    .values("id", "rating", "email", "nickname")
                ),
                "files": [
                    {
                        "id": i.id,
                        "file_name": i.files.name,
                        "files": "http://127.0.0.1:8000" + i.files.url if settings.DEBUG else i.files.url,
                    }
                    for i in project.files.all()
                    if i.files
                ],
                "memo": list(project.memos.all().values("id", "date", "memo")),
            }
            
            #   (3 ) -  
            # cache.set(cache_key, result, 180)
            logger.info(f"Cached project detail for project: {project_id}, user: {user.email}")
            
            return JsonResponse({"result": result}, status=200)
        except Exception as e:
            logger.error(f"Error in ProjectDetail GET: {str(e)}", exc_info=True)
            
            #     
            if "invitations" in str(e):
                logger.error("    -    ")
                return JsonResponse({"message": "     ."}, status=500)
            elif "members" in str(e):
                logger.error("   ")
                return JsonResponse({"message": "     ."}, status=500)
            elif "feedback" in str(e):
                logger.error("   ")
                return JsonResponse({"message": "     ."}, status=500)
            else:
                logger.error(f" : {str(e)}")
                return JsonResponse({"message": f"    : {str(e)}"}, status=500)

    @user_validator
    def post(self, request, project_id):
        try:
            user = request.user
            files = request.FILES.getlist("files")
            inputs = json.loads(request.POST.get("inputs"))
            process = json.loads(request.POST.get("process"))
            members = json.loads(request.POST.get("members"))

            project = models.Project.objects.get_or_none(id=project_id)

            if project is None:
                return JsonResponse({"message": "    ."}, status=404)

            is_member = models.Members.objects.get_or_none(project=project, user=user, rating="manager")
            if project.user != user and is_member is None:
                return StandardResponse.forbidden()

            with transaction.atomic():
                for k, v in inputs.items():
                    setattr(project, k, v)
                project.save()
                for i in process:
                    key = i.get("key")
                    start_date = i.get("startDate")
                    end_date = i.get("endDate")
                    get_process = getattr(project, key)

                    setattr(get_process, "start_date", start_date)
                    setattr(get_process, "end_date", end_date)
                    get_process.save()

                file_list = []
                for f in files:
                    file_list.append(models.File(project=project, files=f))

                models.File.objects.bulk_create(file_list)

                member_list = []
                for i in members:
                    member_obj = models.Members.objects.get_or_none(id=i["id"])
                    member_obj.rating = i["rating"]
                    member_list.append(member_obj)

                models.Members.objects.bulk_update(member_list, fields=["rating"])

            return JsonResponse({"result": "result"}, status=200)
        except Exception as e:
            logger.error(f"Error in project operation: {str(e)}", exc_info=True)
            logging.info(str(e))
            return StandardResponse.server_error()

    @user_validator
    def delete(self, request, project_id):
        try:
            user = request.user
            logging.info(f"[ProjectDetail.delete] Delete request for project {project_id} by user {user.id} ({user.username})")

            project = models.Project.objects.get_or_none(id=project_id)
            if project is None:
                logging.warning(f"[ProjectDetail.delete] Project {project_id} not found")
                return JsonResponse({"message": "    ."}, status=404)

            logging.info(f"[ProjectDetail.delete] Project owner: {project.user.id}, Requesting user: {user.id}")
            
            #       
            is_owner = project.user == user
            is_manager = models.Members.objects.filter(project=project, user=user, rating="manager").exists()
            
            if not is_owner and not is_manager:
                logging.warning(f"[ProjectDetail.delete] Permission denied for user {user.id} on project {project_id}")
                return JsonResponse({"message": "   ."}, status=403)

            #   -   
            project_name = project.name
            
            #   -   
            logging.info(f"[ProjectDetail.delete] Starting deletion process for project {project_id} ({project_name})")
            
            try:
                # Django CASCADE    
                #      ()
                try:
                    member_count = models.Members.objects.filter(project=project).count()
                    invite_count = models.ProjectInvite.objects.filter(project=project).count()
                    file_count = models.File.objects.filter(project=project).count()
                    memo_count = models.Memo.objects.filter(project=project).count()
                    
                    logging.info(f"[ProjectDetail.delete] Associated data count - Members: {member_count}, Invites: {invite_count}, Files: {file_count}, Memos: {memo_count}")
                except Exception as count_error:
                    logging.warning(f"[ProjectDetail.delete] Error counting associated data: {str(count_error)}")
                
                #   (CASCADE    )
                project.delete()
                
                logging.info(f"[ProjectDetail.delete] Successfully deleted project {project_id} ({project_name})")
                
                return JsonResponse({
                    "message": "  .",
                    "project_name": project_name
                }, status=200)
                
            except Exception as delete_error:
                logging.error(f"[ProjectDetail.delete] Error during project deletion: {str(delete_error)}")
                logging.error(f"[ProjectDetail.delete] Error type: {type(delete_error).__name__}")
                
                #    
                error_info = {
                    "error_type": type(delete_error).__name__,
                    "error_message": str(delete_error),
                }
                
                # IntegrityError     
                if "IntegrityError" in str(type(delete_error)):
                    error_info["suggestion"] = "     "
                elif "DoesNotExist" in str(type(delete_error)):
                    error_info["suggestion"] = "    "
                else:
                    error_info["suggestion"] = "   "
                
                raise delete_error
        except Exception as e:
            logging.error(f"[ProjectDetail.delete] Error deleting project {project_id}: {str(e)}")
            logging.error(f"[ProjectDetail.delete] Error type: {type(e).__name__}")
            import traceback
            logging.error(f"[ProjectDetail.delete] Traceback: {traceback.format_exc()}")
            
            #       ()
            error_details = {
                "message": "    .",
                "error_type": type(e).__name__,
                "error_detail": str(e),
                "project_id": project_id
            }
            
            #      
            if settings.DEBUG:
                error_details["traceback"] = traceback.format_exc()
            
            return JsonResponse(error_details, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ProjectFile(View):
    @user_validator
    def delete(self, request, file_id):
        try:
            user = request.user
            # data = json.loads(request.body)

            file_obj = models.File.objects.get_or_none(id=file_id)
            project = file_obj.project

            if project is None or file_obj is None:
                return StandardResponse.server_error()

            is_member = models.Members.objects.get_or_none(project=project, user=user, rating="manager")
            if project.user != user and is_member is None:
                return StandardResponse.forbidden()

            file_obj.delete()
            return StandardResponse.success(message="")
        except Exception as e:
            logger.error(f"Error in project operation: {str(e)}", exc_info=True)
            logging.info(str(e))
            return StandardResponse.server_error()


@method_decorator(csrf_exempt, name='dispatch')
class ProjectMemo(View):
    @user_validator
    def post(self, request, id):
        try:
            user = request.user

            # N+1  :    
            project = models.Project.objects.select_related(
                "user",
                "basic_plan",
                "story_board",
                "filming",
                "video_edit",
                "post_work",
                "video_preview",
                "confirmation",
                "video_delivery"
            ).prefetch_related(
                "members__user",
                "feedbacks__user",
                "files",
                "memos"
            ).filter(id=id).first()
            if project is None:
                return JsonResponse({"message": "    ."}, status=404)

            is_member = models.Members.objects.get_or_none(project=project, user=user, rating="manager")
            if project.user != user and is_member is None:
                return StandardResponse.forbidden()

            data = json.loads(request.body)

            date = data.get("date")

            memo = data.get("memo")
            if date and memo:
                models.Memo.objects.create(project=project, date=date, memo=memo)

            return StandardResponse.success(message="")

        except Exception as e:
            logger.error(f"Error in project operation: {str(e)}", exc_info=True)
            logging.info(str(e))
            return StandardResponse.server_error()

    @user_validator
    def delete(self, request, id):
        try:
            user = request.user
            # N+1  :    
            project = models.Project.objects.select_related(
                "user",
                "basic_plan",
                "story_board",
                "filming",
                "video_edit",
                "post_work",
                "video_preview",
                "confirmation",
                "video_delivery"
            ).prefetch_related(
                "members__user",
                "feedbacks__user",
                "files",
                "memos"
            ).filter(id=id).first()

            data = json.loads(request.body)
            memo_id = data.get("memo_id")
            memo = models.Memo.objects.get_or_none(id=memo_id)
            if memo is None:
                return JsonResponse({"message": "    ."}, status=404)
            if project is None:
                return JsonResponse({"message": "    ."}, status=404)

            is_member = models.Members.objects.get_or_none(project=project, user=user, rating="manager")
            if project.user != user and is_member is None:
                return StandardResponse.forbidden()

            memo.delete()

            return StandardResponse.success(message="")
        except Exception as e:
            logger.error(f"Error in project operation: {str(e)}", exc_info=True)
            logging.info(str(e))
            return StandardResponse.server_error()


@method_decorator(csrf_exempt, name='dispatch')
class ProjectDate(View):
    @user_validator
    def post(self, request, id):
        try:
            user = request.user

            # N+1  :    
            project = models.Project.objects.select_related(
                "user",
                "basic_plan",
                "story_board",
                "filming",
                "video_edit",
                "post_work",
                "video_preview",
                "confirmation",
                "video_delivery"
            ).prefetch_related(
                "members__user",
                "feedbacks__user",
                "files",
                "memos"
            ).filter(id=id).first()
            if project is None:
                return JsonResponse({"message": "    ."}, status=404)

            is_member = models.Members.objects.get_or_none(project=project, user=user, rating="manager")
            if project.user != user and is_member is None:
                return StandardResponse.forbidden()

            data = json.loads(request.body)
            key = data.get("key")
            start_date = data.get("start_date")
            end_date = data.get("end_date")

            get_process = getattr(project, key)
            setattr(get_process, "start_date", start_date)
            setattr(get_process, "end_date", end_date)
            get_process.save()

            return StandardResponse.success(message="")

        except Exception as e:
            logger.error(f"Error in project operation: {str(e)}", exc_info=True)
            logging.info(str(e))
            return StandardResponse.server_error()



#    
@method_decorator(csrf_exempt, name="dispatch")
class ProjectFeedback(View):
    """    """
    
    @user_validator
    def get(self, request, project_id):
        try:
            user = request.user
            # N+1  :     
            project = models.Project.objects.select_related(
                "user"
            ).prefetch_related(
                "feedbacks__user",
                "feedbacks__comments__user",
                "members__user"
            ).filter(id=project_id).first()
            
            if project is None:
                return StandardResponse.not_found("")
            
            #   -    
            is_member = models.Members.objects.filter(project=project, user=user).exists()
            if project.user != user and not is_member:
                return StandardResponse.forbidden()
            
            #     
            if not project.feedback:
                return JsonResponse({
                    "result": {
                        "id": None,
                        "project": project_id,
                        "files": None,
                        "comments": []
                    }
                }, status=200)
            
            #   
            feedback = project.feedback
            
            #  URL  -  URL 
            file_url = None
            if feedback.files:
                if hasattr(feedback.files, 'url'):
                    file_url = feedback.files.url
                    # URL     URL 
                    if file_url and not file_url.startswith('http'):
                        #    
                        if settings.DEBUG:
                            file_url = f"http://localhost:8000{file_url}"
                        else:
                            # Railway   
                            backend_url = os.environ.get('BACKEND_URL', 'https://videoplanet.up.railway.app')
                            # URL  /     
                            if backend_url.endswith('/'):
                                backend_url = backend_url.rstrip('/')
                            file_url = f"{backend_url}{file_url}"
                    logger.info(f"Generated file URL: {file_url}")
            
            result = {
                "id": feedback.id,
                "project": project_id,
                "files": file_url,
                "created": feedback.created,
                "updated": feedback.updated,
                "comments": []
            }
            
            #   
            comments = feedback_model.FeedBackComment.objects.filter(
                feedback=feedback
            ).order_by("-created")
            
            for comment in comments:
                result["comments"].append({
                    "id": comment.id,
                    "section": comment.section,
                    "title": comment.title,
                    "text": comment.text,
                    "security": comment.security,
                    "user": comment.user.email if not comment.security else "",
                    "created": comment.created
                })
            
            return JsonResponse({"result": result}, status=200)
            
        except Exception as e:
            logger.error(f"Error in project feedback: {str(e)}", exc_info=True)
            return JsonResponse({"message": f" : {str(e)}"}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class ProjectFeedbackComments(View):
    """      """
    
    @user_validator
    def get(self, request, project_id):
        #  ProjectFeedback.get    
        #    
        return JsonResponse({"message": "Use /api/projects/{project_id}/feedback/ endpoint"}, status=200)
    
    @user_validator
    def post(self, request, project_id):
        try:
            user = request.user
            # N+1  :     
            project = models.Project.objects.select_related(
                "user"
            ).prefetch_related(
                "feedbacks__user",
                "feedbacks__comments__user",
                "members__user"
            ).filter(id=project_id).first()
            
            if project is None:
                return StandardResponse.not_found("")
            
            #  
            is_member = models.Members.objects.filter(project=project, user=user).exists()
            if project.user != user and not is_member:
                return StandardResponse.forbidden()
            
            #   
            if not project.feedback:
                return JsonResponse({"message": " ."}, status=404)
            
            data = json.loads(request.body)
            
            #  
            comment = feedback_model.FeedBackComment.objects.create(
                feedback=project.feedback,
                user=user,
                section=data.get("section", ""),
                title=data.get("title", ""),
                text=data.get("text", ""),
                security=data.get("security", False)
            )
            
            return JsonResponse({
                "result": {
                    "id": comment.id,
                    "section": comment.section,
                    "title": comment.title,
                    "text": comment.text,
                    "security": comment.security,
                    "user": comment.user.email if not comment.security else "",
                    "created": comment.created
                }
            }, status=201)
            
        except Exception as e:
            logger.error(f"Error in feedback comments: {str(e)}", exc_info=True)
            return JsonResponse({"message": f" : {str(e)}"}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class ProjectFeedbackUpload(View):
    """   """
    
    @user_validator
    def post(self, request, project_id):
        try:
            user = request.user
            # N+1  :     
            project = models.Project.objects.select_related(
                "user"
            ).prefetch_related(
                "feedbacks__user",
                "feedbacks__comments__user",
                "members__user"
            ).filter(id=project_id).first()
            
            if project is None:
                return StandardResponse.not_found("")
            
            #   -    
            is_manager = models.Members.objects.filter(
                project=project, 
                user=user, 
                rating="manager"
            ).exists()
            
            if project.user != user and not is_manager:
                return StandardResponse.forbidden()
            
            #  
            file = request.FILES.get("files") or request.FILES.get("file")
            if not file:
                return JsonResponse({"message": " ."}, status=400)
            
            #   
            if not project.feedback:
                feedback = feedback_model.FeedBack.objects.create()
                project.feedback = feedback
                project.save()
            else:
                feedback = project.feedback
            
            #    
            if feedback.files:
                feedback.files.delete()
            
            #   
            feedback.files = file
            feedback.save()
            
            #  URL  -  URL 
            file_url = feedback.files.url
            if file_url and not file_url.startswith('http'):
                if settings.DEBUG:
                    file_url = f"http://localhost:8000{file_url}"
                else:
                    backend_url = os.environ.get('BACKEND_URL', 'https://videoplanet.up.railway.app')
                    if backend_url.endswith('/'):
                        backend_url = backend_url.rstrip('/')
                    file_url = f"{backend_url}{file_url}"
            
            logger.info(f"Upload complete. File URL: {file_url}")
            
            return JsonResponse({
                "result": {
                    "id": feedback.id,
                    "file_url": file_url
                }
            }, status=200)
            
        except Exception as e:
            logger.error(f"Error in feedback upload: {str(e)}", exc_info=True)
            return JsonResponse({"message": f" : {str(e)}"}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class ProjectFeedbackEncodingStatus(View):
    """   """
    
    @user_validator
    def get(self, request, project_id):
        try:
            user = request.user
            # N+1  :     
            project = models.Project.objects.select_related(
                "user"
            ).prefetch_related(
                "feedbacks__user",
                "feedbacks__comments__user",
                "members__user"
            ).filter(id=project_id).first()
            
            if project is None:
                return StandardResponse.not_found("")
            
            #  
            is_member = models.Members.objects.filter(project=project, user=user).exists()
            if project.user != user and not is_member:
                return StandardResponse.forbidden()
            
            #     
            if not project.feedback or not project.feedback.files:
                return JsonResponse({
                    "status": "no_file",
                    "message": "  ."
                }, status=200)
            
            #      
            #     
            return JsonResponse({
                "status": "completed",
                "message": " .",
                "file_url": project.feedback.files.url
            }, status=200)
            
        except Exception as e:
            logger.error(f"Error in encoding status: {str(e)}", exc_info=True)
            return JsonResponse({"message": f" : {str(e)}"}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ProjectInvitation(View):
    """  """
    
    @user_validator
    def get(self, request, project_id=None):
        """  """
        try:
            user = request.user
            
            # project_id     
            if project_id:
                project = models.Project.objects.filter(id=project_id).first()
                if not project:
                    return StandardResponse.not_found("")
                
                #  
                is_owner = project.user == user
                is_manager = models.Members.objects.filter(project=project, user=user, rating="manager").exists()
                
                if not is_owner and not is_manager:
                    return JsonResponse({"message": "  ."}, status=403)
                
                #    
                invitations = models.ProjectInvitation.objects.filter(
                    project=project,
                    status='pending'
                ).order_by('-created_at')
                
                result = []
                for invitation in invitations:
                    result.append({
                        "id": invitation.id,
                        "invitee_email": invitation.invitee_email,
                        "message": invitation.message,
                        "created_at": invitation.created_at,
                        "expires_at": invitation.expires_at,
                        "inviter_name": invitation.inviter.nickname or invitation.inviter.username
                    })
                
                return JsonResponse({"invitations": result}, status=200)
            
            # project_id      
            else:
                #  
                sent_invitations = models.ProjectInvitation.objects.filter(
                    inviter=user,
                    status='pending'
                ).select_related('project').order_by('-created_at')
                
                sent_list = []
                for invitation in sent_invitations:
                    sent_list.append({
                        "id": invitation.id,
                        "project_name": invitation.project.name,
                        "invitee_email": invitation.invitee_email,
                        "created_at": invitation.created_at,
                        "expires_at": invitation.expires_at,
                        "status": invitation.status
                    })
                
                #  
                received_invitations = models.ProjectInvitation.objects.filter(
                    invitee_email=user.email,
                    status='pending'
                ).select_related('project', 'inviter').order_by('-created_at')
                
                received_list = []
                for invitation in received_invitations:
                    received_list.append({
                        "id": invitation.id,
                        "project_name": invitation.project.name,
                        "inviter_name": invitation.inviter.nickname or invitation.inviter.username,
                        "inviter_email": invitation.inviter.email,
                        "message": invitation.message,
                        "created_at": invitation.created_at,
                        "expires_at": invitation.expires_at
                    })
                
                #   
                recent_accepted = models.ProjectInvitation.objects.filter(
                    invitee_email=user.email,
                    status='accepted'
                ).select_related('project', 'inviter').order_by('-updated_at')[:5]
                
                recent_accepted_list = []
                for invitation in recent_accepted:
                    recent_accepted_list.append({
                        "id": invitation.id,
                        "project_name": invitation.project.name,
                        "inviter_name": invitation.inviter.nickname or invitation.inviter.username,
                        "accepted_at": invitation.updated_at
                    })
                
                return JsonResponse({
                    "sent": sent_list,
                    "received": received_list,
                    "recent_accepted": recent_accepted_list
                }, status=200)
                
        except Exception as e:
            logger.error(f"    : {str(e)}")
            return JsonResponse({"message": "     ."}, status=500)
    
    @user_validator
    def delete(self, request, project_id):
        """ """
        try:
            user = request.user
            data = json.loads(request.body)
            
            invitation_id = data.get('invitation_id')
            
            if not invitation_id:
                return JsonResponse({"message": " ID ."}, status=400)
            
            #  
            invitation = models.ProjectInvitation.objects.filter(
                id=invitation_id,
                project_id=project_id
            ).first()
            
            if not invitation:
                return JsonResponse({"message": "   ."}, status=404)
            
            #   (  )
            if invitation.inviter != user:
                return JsonResponse({"message": "   ."}, status=403)
            
            #     
            if invitation.status != 'pending':
                return JsonResponse({"message": f" {invitation.get_status_display()}    ."}, status=400)
            
            #  
            invitation.status = 'cancelled'
            invitation.save()
            
            #       
            try:
                if invitation.invitee:
                    from users.models import Notification
                    Notification.objects.create(
                        recipient=invitation.invitee,
                        notification_type='invitation_cancelled',
                        title=' ',
                        message=f'{invitation.inviter.nickname} "{invitation.project.name}"   .',
                        project_id=invitation.project.id
                    )
            except Exception as e:
                logger.error(f"     : {str(e)}")
            
            return JsonResponse({"message": " ."}, status=200)
            
        except Exception as e:
            logger.error(f"   : {str(e)}")
            return JsonResponse({"message": "    ."}, status=500)

    @user_validator
    def post(self, request, project_id):
        """  """
        try:
            user = request.user
            data = json.loads(request.body)
            
            #   
            email = data.get('email')
            message = data.get('message', '')
            
            if not email:
                return JsonResponse({"message": " ."}, status=400)
            
            #  
            project = models.Project.objects.filter(id=project_id).first()
            if not project:
                return StandardResponse.not_found("")
            
            #   (     )
            is_owner = project.user == user
            is_manager = models.Members.objects.filter(project=project, user=user, rating="manager").exists()
            
            if not is_owner and not is_manager:
                return JsonResponse({"message": "  ."}, status=403)
            
            #   
            User = get_user_model()
            invitee_user = User.objects.filter(email=email).first()
            if invitee_user and models.Members.objects.filter(project=project, user=invitee_user).exists():
                return JsonResponse({"message": "  ."}, status=400)
            
            #   
            existing_invitation = models.ProjectInvitation.objects.filter(
                project=project,
                invitee_email=email,
                status='pending'
            ).first()
            
            if existing_invitation:
                #   
                resend = data.get('resend', False)
                if resend:
                    #     
                    existing_invitation.updated = django_timezone.now()
                    existing_invitation.save()
                    
                    #  
                    email_sent = False
                    email_error = None
                    try:
                        #    
                        from .email_service import ProjectInvitationEmailService
                        email_sent = ProjectInvitationEmailService.send_invitation_email(invitation)
                        if email_sent:
                            logger.info(f"   : {email}")
                        else:
                            logger.warning(f"   : {email}")
                            email_error = "  ."
                    except Exception as e:
                        logger.error(f"    : {str(e)}")
                        email_sent = False
                        email_error = str(e)
                    
                    return JsonResponse({
                        "message": "  ." if email_sent else "   .",
                        "invitation_id": existing_invitation.id,
                        "email_sent": email_sent,
                        "email_error": email_error,
                        "resent": True
                    }, status=200)
                else:
                    return JsonResponse({
                        "message": "  .",
                        "invitation_exists": True,
                        "invitation_id": existing_invitation.id
                    }, status=409)  # 409 Conflict
            
            #   
            token = secrets.token_urlsafe(32)
            
            #  
            invitation = models.ProjectInvitation.objects.create(
                project=project,
                inviter=user,
                invitee_email=email,
                message=message,
                token=token,
                expires_at=django_timezone.now() + timedelta(days=7),  # 7  
                invitee=invitee_user if invitee_user else None
            )
            
            #     
            
            #   (    )
            email_sent = False
            email_error = None
            try:
                #   -    
                try:
                    from .email_service import ProjectInvitationEmailService
                    email_sent = ProjectInvitationEmailService.send_invitation_email(invitation)
                    if email_sent:
                        logger.info(f"   : {email}")
                    else:
                        logger.warning(f"   : {email}")
                        email_error = "  ."
                except Exception as e:
                    logger.error(f"    : {str(e)}")
                    #       
                    email_error = "  ."
            except Exception as e:
                logger.error(f"    : {str(e)}")
                email_sent = False
                email_error = str(e)
            
            #   (  )
            try:
                if invitee_user:
                    from users.models import Notification
                    Notification.objects.create(
                        recipient=invitee_user,
                        notification_type='invitation_received',
                        title='  ',
                        message=f'{user.nickname or user.username} "{project.name}"  .',
                        project_id=project.id,
                        invitation_id=invitation.id
                    )
                    logger.info(f"   : {email}")
            except Exception as e:
                logger.error(f"    : {str(e)}")
            
            #    
            try:
                from users.models import RecentInvitation
                recent_invitation, created = RecentInvitation.objects.get_or_create(
                    inviter=user,
                    invitee_email=email,
                    defaults={
                        'invitee_name': invitee_user.nickname if invitee_user else '',
                        'project_name': project.name,
                        'invitation_count': 1
                    }
                )
                
                if not created:
                    #     
                    recent_invitation.invitation_count += 1
                    recent_invitation.project_name = project.name  #   
                    recent_invitation.save()
            except Exception as e:
                logger.error(f"     : {str(e)}")
            
            #      
            # try:
            #     if hasattr(settings, 'EMAIL_HOST') and settings.EMAIL_HOST:
            #         invitation_url = f"{settings.FRONTEND_URL}/invitation/{token}"
            #         send_mail(
            #             subject=f' "{project.name}" ',
            #             message=f'{user.nickname or user.username}  "{project.name}" .\n\n'
            #                    f': {message}\n\n'
            #                    f' : {invitation_url}',
            #             from_email=settings.DEFAULT_FROM_EMAIL,
            #             recipient_list=[email],
            #             fail_silently=True,
            #         )
            # except Exception as e:
            #     logger.warning(f"Failed to send invitation email: {str(e)}")
            
            #   
            response_data = {
                "invitation_id": invitation.id,
                "email_sent": email_sent
            }
            
            if email_sent:
                response_data["message"] = " .  ."
            else:
                response_data["message"] = "    ."
                if email_error:
                    response_data["email_error"] = email_error
            
            return JsonResponse(response_data, status=201)
            
        except Exception as e:
            logger.error(f"Error in project invitation: {str(e)}", exc_info=True)
            return JsonResponse({"message": f"   : {str(e)}"}, status=500)
    
    @user_validator
    def get(self, request, project_id=None):
        """  """
        try:
            logger.info(f"ProjectInvitation GET request from user: {request.user.email}, project_id: {project_id}")
            user = request.user
            
            #     (   )
            return JsonResponse({
                "sent_invitations": [],
                "received_invitations": []
            }, status=200)
            
            if project_id:
                #    
                project = models.Project.objects.filter(id=project_id).first()
                if not project:
                    return StandardResponse.not_found("")
                
                #  
                is_owner = project.user == user
                is_manager = models.Members.objects.filter(project=project, user=user, rating="manager").exists()
                
                if not is_owner and not is_manager:
                    return JsonResponse({"message": "  ."}, status=403)
                
                invitations = models.ProjectInvitation.objects.filter(project=project).order_by('-created')
            else:
                #    (  +  )
                # ProjectInvitation    
                try:
                    # select_related    
                    sent_invitations = models.ProjectInvitation.objects.filter(
                        inviter=user
                    ).order_by('-created')
                    
                    received_invitations = models.ProjectInvitation.objects.filter(
                        invitee=user
                    ).order_by('-created')
                    
                    #     
                    received_by_email = models.ProjectInvitation.objects.filter(
                        invitee_email=user.email
                    ).order_by('-created')
                except Exception as e:
                    logger.error(f"Error accessing ProjectInvitation model: {str(e)}", exc_info=True)
                    #      
                    sent_invitations = []
                    received_invitations = []
                    received_by_email = []
                
                result = {
                    "sent_invitations": [
                        {
                            "id": inv.id,
                            "project_name": getattr(inv.project, 'name', 'Unknown Project'),
                            "project_id": getattr(inv.project, 'id', None),
                            "invitee_email": inv.invitee_email,
                            "message": inv.message,
                            "status": inv.status,
                            "created": inv.created.isoformat() if inv.created else None,
                            "expires_at": inv.expires_at.isoformat() if inv.expires_at else None,
                        }
                        for inv in sent_invitations if inv
                    ],
                    "received_invitations": [
                        {
                            "id": inv.id,
                            "project_name": getattr(inv.project, 'name', 'Unknown Project'),
                            "project_id": getattr(inv.project, 'id', None),
                            "inviter_name": getattr(inv.inviter, 'nickname', '') or getattr(inv.inviter, 'username', 'Unknown'),
                            "message": inv.message,
                            "status": inv.status,
                            "created": inv.created.isoformat() if inv.created else None,
                            "expires_at": inv.expires_at.isoformat() if inv.expires_at else None,
                        }
                        for inv in list(received_invitations) + list(received_by_email)
                    ]
                }
                
                return JsonResponse(result, status=200)
            
            #    
            invitations_data = [
                {
                    "id": inv.id,
                    "invitee_email": inv.invitee_email,
                    "inviter_name": inv.inviter.nickname or inv.inviter.username,
                    "message": inv.message,
                    "status": inv.status,
                    "created": inv.created.isoformat(),
                    "expires_at": inv.expires_at.isoformat(),
                }
                for inv in invitations
            ]
            
            return JsonResponse({"invitations": invitations_data}, status=200)
            
        except Exception as e:
            logger.error(f"Error in invitation list: {str(e)}", exc_info=True)
            return JsonResponse({"message": f"     : {str(e)}"}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class InvitationToken(View):
    """   """
    
    def get(self, request, token):
        """    ( )"""
        try:
            #   
            invitation = models.ProjectInvitation.objects.filter(token=token).first()
            
            if not invitation:
                return JsonResponse({"status": "error", "message": "   ."}, status=404)
            
            #  
            if invitation.expires_at < django_timezone.now():
                return JsonResponse({"status": "error", "message": "  ."}, status=400)
            
            #    
            if invitation.status != 'pending':
                status_text = {
                    'accepted': ' ',
                    'declined': '',
                    'cancelled': ''
                }.get(invitation.status, '')
                return JsonResponse({"status": "error", "message": f"{status_text} ."}, status=400)
            
            #    (  )
            invitation_data = {
                "id": invitation.id,
                "project": {
                    "id": invitation.project.id,
                    "name": invitation.project.name,
                    "description": invitation.project.description,
                    "created": invitation.project.created
                },
                "inviter": {
                    "nickname": invitation.inviter.nickname or invitation.inviter.username,
                    "email": invitation.inviter.email
                },
                "invitee_email": invitation.invitee_email,
                "message": invitation.message,
                "created": invitation.created,
                "expires_at": invitation.expires_at,
                "status": invitation.status
            }
            
            return JsonResponse({
                "status": "success",
                "invitation": invitation_data
            }, status=200)
            
        except Exception as e:
            logger.error(f"     : {str(e)}")
            return JsonResponse({"status": "error", "message": "     ."}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class InvitationResponse(View):
    """ /"""
    
    def post(self, request, invitation_id):
        """ /"""
        try:
            #   (   )
            user = request.user if request.user.is_authenticated else None
            data = json.loads(request.body)
            
            action = data.get('action')  # 'accept' or 'decline'
            
            if action not in ['accept', 'decline']:
                return JsonResponse({"message": " ."}, status=400)
            
            #  
            invitation = models.ProjectInvitation.objects.filter(id=invitation_id).first()
            if not invitation:
                return JsonResponse({"message": "   ."}, status=404)
            
            #   (  / )
            #    
            if user:
                if invitation.invitee != user and invitation.invitee_email != user.email:
                    return StandardResponse.forbidden()
            else:
                #        
                pass
            
            #    
            if invitation.status != 'pending':
                return JsonResponse({"message": f" {invitation.get_status_display()} ."}, status=400)
            
            #   
            if invitation.expires_at < django_timezone.now():
                invitation.status = 'expired'
                invitation.save()
                return JsonResponse({"message": " ."}, status=400)
            
            #  
            from .email_service import ProjectInvitationEmailService
            from .notification_service import NotificationService
            
            if action == 'accept':
                #    
                if not user:
                    return JsonResponse({"message": "   ."}, status=401)
                
                #   
                member, created = models.Members.objects.get_or_create(
                    project=invitation.project,
                    user=user,
                    defaults={'rating': 'member'}
                )
                
                invitation.status = 'accepted'
                invitation.accepted_at = django_timezone.now()
                invitation.invitee = user  #  
                invitation.save()
                
                #     
                try:
                    #  
                    NotificationService.notify_invitation_accepted(invitation)
                    #  
                    ProjectInvitationEmailService.send_invitation_accepted_email(invitation)
                    #      
                    NotificationService.notify_member_joined(invitation.project, user)
                except Exception as e:
                    logger.error(f"  /   : {str(e)}")
                
                return JsonResponse({"message": " ."}, status=200)
            
            else:  # decline
                invitation.status = 'declined'
                invitation.declined_at = django_timezone.now()
                if user:
                    invitation.invitee = user  #  
                invitation.save()
                
                #     
                try:
                    #  
                    NotificationService.notify_invitation_declined(invitation)
                    #  
                    ProjectInvitationEmailService.send_invitation_declined_email(invitation)
                except Exception as e:
                    logger.error(f"  /   : {str(e)}")
                
                #    
                # from users.models import Notification
                # Notification.objects.create(
                #     recipient=invitation.inviter,
                #     notification_type='invitation_declined',
                #     title=f' ',
                #     message=f'{user.nickname or user.username}  "{invitation.project.name}"  .',
                #     project_id=invitation.project.id,
                #     invitation_id=invitation.id,
                #     extra_data={
                #         'decliner_name': user.nickname or user.username,
                #         'project_name': invitation.project.name
                #     }
                # )
                
                return JsonResponse({"message": " ."}, status=200)
            
        except Exception as e:
            logger.error(f"Error in invitation response: {str(e)}", exc_info=True)
            return JsonResponse({"message": f"    : {str(e)}"}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class DevelopmentFrameworkList(View):
    """      """
    
    @user_validator
    def get(self, request):
        try:
            user = request.user
            frameworks = models.DevelopmentFramework.objects.filter(user=user).order_by('-is_default', '-created')
            
            result = []
            for framework in frameworks:
                result.append({
                    "id": framework.id,
                    "name": framework.name,
                    "intro_hook": framework.intro_hook,
                    "immersion": framework.immersion,
                    "twist": framework.twist,
                    "hook_next": framework.hook_next,
                    "is_default": framework.is_default,
                    "created": framework.created,
                    "updated": framework.updated,
                })
            
            return JsonResponse({
                "frameworks": result,
                "count": len(result)
            }, status=200)
            
        except Exception as e:
            logger.error(f"Error in DevelopmentFrameworkList GET: {str(e)}", exc_info=True)
            return JsonResponse({"message": "     ."}, status=500)
    
    @user_validator
    def post(self, request):
        try:
            user = request.user
            data = json.loads(request.body)
            
            #   
            required_fields = ['name', 'intro_hook', 'immersion', 'twist', 'hook_next']
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({"message": f"{field}  ."}, status=400)
            
            #  
            framework = models.DevelopmentFramework.objects.create(
                user=user,
                name=data['name'],
                intro_hook=data['intro_hook'],
                immersion=data['immersion'],
                twist=data['twist'],
                hook_next=data['hook_next'],
                is_default=data.get('is_default', False)
            )
            
            return JsonResponse({
                "message": "  .",
                "framework": {
                    "id": framework.id,
                    "name": framework.name,
                    "intro_hook": framework.intro_hook,
                    "immersion": framework.immersion,
                    "twist": framework.twist,
                    "hook_next": framework.hook_next,
                    "is_default": framework.is_default,
                    "created": framework.created,
                    "updated": framework.updated,
                }
            }, status=201)
            
        except Exception as e:
            logger.error(f"Error in DevelopmentFrameworkList POST: {str(e)}", exc_info=True)
            return JsonResponse({"message": "    ."}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class DevelopmentFrameworkDetail(View):
    """    , , """
    
    @user_validator
    def get(self, request, framework_id):
        try:
            user = request.user
            framework = models.DevelopmentFramework.objects.get(id=framework_id, user=user)
            
            return JsonResponse({
                "id": framework.id,
                "name": framework.name,
                "intro_hook": framework.intro_hook,
                "immersion": framework.immersion,
                "twist": framework.twist,
                "hook_next": framework.hook_next,
                "is_default": framework.is_default,
                "created": framework.created,
                "updated": framework.updated,
            }, status=200)
            
        except models.DevelopmentFramework.DoesNotExist:
            return JsonResponse({"message": "   ."}, status=404)
        except Exception as e:
            logger.error(f"Error in DevelopmentFrameworkDetail GET: {str(e)}", exc_info=True)
            return JsonResponse({"message": "    ."}, status=500)
    
    @user_validator
    def put(self, request, framework_id):
        try:
            user = request.user
            framework = models.DevelopmentFramework.objects.get(id=framework_id, user=user)
            data = json.loads(request.body)
            
            #  
            update_fields = ['name', 'intro_hook', 'immersion', 'twist', 'hook_next', 'is_default']
            for field in update_fields:
                if field in data:
                    setattr(framework, field, data[field])
            
            framework.save()
            
            return JsonResponse({
                "message": "  .",
                "framework": {
                    "id": framework.id,
                    "name": framework.name,
                    "intro_hook": framework.intro_hook,
                    "immersion": framework.immersion,
                    "twist": framework.twist,
                    "hook_next": framework.hook_next,
                    "is_default": framework.is_default,
                    "created": framework.created,
                    "updated": framework.updated,
                }
            }, status=200)
            
        except models.DevelopmentFramework.DoesNotExist:
            return JsonResponse({"message": "   ."}, status=404)
        except Exception as e:
            logger.error(f"Error in DevelopmentFrameworkDetail PUT: {str(e)}", exc_info=True)
            return JsonResponse({"message": "    ."}, status=500)
    
    @user_validator
    def delete(self, request, framework_id):
        try:
            user = request.user
            framework = models.DevelopmentFramework.objects.get(id=framework_id, user=user)
            
            #    
            if framework.is_default:
                #    
                other_frameworks = models.DevelopmentFramework.objects.filter(user=user).exclude(id=framework_id)
                if not other_frameworks.exists():
                    return JsonResponse({"message": "    ."}, status=400)
                
                #    
                other_frameworks.first().is_default = True
                other_frameworks.first().save()
            
            framework.delete()
            
            return JsonResponse({"message": "  ."}, status=200)
            
        except models.DevelopmentFramework.DoesNotExist:
            return JsonResponse({"message": "   ."}, status=404)
        except Exception as e:
            logger.error(f"Error in DevelopmentFrameworkDetail DELETE: {str(e)}", exc_info=True)
            return JsonResponse({"message": "    ."}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class SetDefaultFramework(View):
    """   API"""
    
    @user_validator
    def post(self, request, framework_id):
        try:
            user = request.user
            framework = models.DevelopmentFramework.objects.get(id=framework_id, user=user)
            
            #    
            models.DevelopmentFramework.objects.filter(user=user, is_default=True).update(is_default=False)
            
            #    
            framework.is_default = True
            framework.save()
            
            return JsonResponse({
                "message": "  .",
                "framework_id": framework.id,
                "framework_name": framework.name
            }, status=200)
            
        except models.DevelopmentFramework.DoesNotExist:
            return JsonResponse({"message": "   ."}, status=404)
        except Exception as e:
            logger.error(f"Error in SetDefaultFramework: {str(e)}", exc_info=True)
            return JsonResponse({"message": "     ."}, status=500)

