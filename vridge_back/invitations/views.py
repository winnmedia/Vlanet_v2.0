from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from django.utils import timezone
from .models import Invitation, TeamMember, InvitationFriend
from .serializers import (
    InvitationSerializer, SendInvitationSerializer,
    UpdateInvitationSerializer, TeamMemberSerializer,
    FriendSerializer, InvitationStatsSerializer,
    UserSearchSerializer
)
from projects.models import Project
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class SendInvitation(APIView):
    """ """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            serializer = SendInvitationSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            data = serializer.validated_data
            
            #     
            existing = Invitation.objects.filter(
                sender=request.user,
                recipient_email=data['recipient_email'],
                status='pending'
            ).first()
            
            if existing and not existing.is_expired():
                return Response(
                    {"error": "    ."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            #   ()
            project = None
            if 'project_id' in data and data['project_id']:
                try:
                    project = Project.objects.get(id=data['project_id'], user=request.user)
                except Project.DoesNotExist:
                    return Response(
                        {"error": "   ."},
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            #  
            invitation = Invitation.objects.create(
                sender=request.user,
                recipient_email=data['recipient_email'],
                project=project,
                message=data.get('message', '')
            )
            
            # TODO:    
            
            serializer = InvitationSerializer(invitation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Send invitation error: {str(e)}")
            return Response(
                {"error": "    ."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ReceivedInvitations(generics.ListAPIView):
    """  """
    serializer_class = InvitationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Invitation.objects.filter(
            recipient_email=self.request.user.email
        ).select_related('sender', 'project').order_by('-created_at')


class SentInvitations(generics.ListAPIView):
    """  """
    serializer_class = InvitationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Invitation.objects.filter(
            sender=self.request.user
        ).select_related('project').order_by('-created_at')


class InvitationDetail(generics.RetrieveAPIView):
    """  """
    serializer_class = InvitationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'
    
    def get_queryset(self):
        return Invitation.objects.filter(
            Q(sender=self.request.user) |
            Q(recipient_email=self.request.user.email)
        ).select_related('sender', 'project')


class RespondToInvitation(APIView):
    """  (/)"""
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, pk):
        try:
            invitation = Invitation.objects.get(
                pk=pk,
                recipient_email=request.user.email,
                status='pending'
            )
            
            if invitation.is_expired():
                return Response(
                    {"error": " ."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = UpdateInvitationSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            data = serializer.validated_data
            invitation.status = data['status']
            invitation.save()
            
            #     
            if data['status'] == 'accepted' and invitation.project:
                TeamMember.objects.get_or_create(
                    user=request.user,
                    project=invitation.project,
                    defaults={'role': 'member'}
                )
            
            # TODO:    
            
            return Response(
                InvitationSerializer(invitation).data,
                status=status.HTTP_200_OK
            )
            
        except Invitation.DoesNotExist:
            return Response(
                {"error": "   ."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Respond to invitation error: {str(e)}")
            return Response(
                {"error": "    ."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CancelInvitation(APIView):
    """ """
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, pk):
        try:
            invitation = Invitation.objects.get(
                pk=pk,
                sender=request.user,
                status='pending'
            )
            
            invitation.status = 'cancelled'
            invitation.save()
            
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Invitation.DoesNotExist:
            return Response(
                {"error": "   ."},
                status=status.HTTP_404_NOT_FOUND
            )


class ResendInvitation(APIView):
    """ """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        try:
            invitation = Invitation.objects.get(
                pk=pk,
                sender=request.user
            )
            
            #   
            invitation.expires_at = timezone.now() + timezone.timedelta(days=7)
            invitation.save()
            
            # TODO:   
            
            return Response(
                InvitationSerializer(invitation).data,
                status=status.HTTP_200_OK
            )
            
        except Invitation.DoesNotExist:
            return Response(
                {"error": "   ."},
                status=status.HTTP_404_NOT_FOUND
            )


class TeamMemberList(generics.ListAPIView):
    """  """
    serializer_class = TeamMemberSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = TeamMember.objects.filter(
            project__user=self.request.user
        ).select_related('user', 'project')
        
        project_id = self.request.query_params.get('project_id')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        return queryset


class RemoveTeamMember(APIView):
    """  """
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, pk):
        try:
            member = TeamMember.objects.get(
                pk=pk,
                project__user=request.user
            )
            
            #    
            if member.role == 'owner':
                return Response(
                    {"error": "   ."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            member.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except TeamMember.DoesNotExist:
            return Response(
                {"error": "    ."},
                status=status.HTTP_404_NOT_FOUND
            )


class FriendList(generics.ListCreateAPIView):
    """친구 목록 조회 및 추가"""
    serializer_class = FriendSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return InvitationFriend.objects.filter(
            user=self.request.user
        ).select_related('friend')
    
    def create(self, request):
        email = request.data.get('email')
        
        try:
            friend_user = User.objects.get(email=email)
            
            if friend_user == request.user:
                return Response(
                    {"error": "자신을 친구로 추가할 수 없습니다."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            friend, created = InvitationFriend.objects.get_or_create(
                user=request.user,
                friend=friend_user
            )
            
            serializer = FriendSerializer(friend)
            status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
            return Response(serializer.data, status=status_code)
            
        except User.DoesNotExist:
            return Response(
                {"error": "사용자를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND
            )


class RemoveFriend(APIView):
    """친구 제거"""
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, pk):
        try:
            friend = InvitationFriend.objects.get(pk=pk, user=request.user)
            friend.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except InvitationFriend.DoesNotExist:
            return Response(
                {"error": "친구를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND
            )


class InvitationStats(APIView):
    """ """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        sent_stats = Invitation.objects.filter(sender=user).aggregate(
            total=Count('id'),
            pending=Count('id', filter=Q(status='pending')),
            accepted=Count('id', filter=Q(status='accepted')),
            declined=Count('id', filter=Q(status='declined'))
        )
        
        received_stats = Invitation.objects.filter(recipient_email=user.email).aggregate(
            total=Count('id'),
            pending=Count('id', filter=Q(status='pending')),
            accepted=Count('id', filter=Q(status='accepted')),
            declined=Count('id', filter=Q(status='declined'))
        )
        
        stats = {
            'total_sent': sent_stats['total'],
            'total_received': received_stats['total'],
            'pending_sent': sent_stats['pending'],
            'pending_received': received_stats['pending'],
            'accepted_sent': sent_stats['accepted'],
            'accepted_received': received_stats['accepted'],
            'declined_sent': sent_stats['declined'],
            'declined_received': received_stats['declined']
        }
        
        serializer = InvitationStatsSerializer(stats)
        return Response(serializer.data)


class AcceptInvitation(APIView):
    """Accept invitation endpoint - POST /api/invitations/{id}/accept/"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        try:
            invitation = Invitation.objects.get(
                pk=pk,
                recipient_email=request.user.email,
                status='pending'
            )
            
            if invitation.is_expired():
                return Response(
                    {"error": "초대가 만료되었습니다."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            invitation.status = 'accepted'
            invitation.save()
            
            # Add user to team if project exists
            if invitation.project:
                TeamMember.objects.get_or_create(
                    user=request.user,
                    project=invitation.project,
                    defaults={'role': 'member'}
                )
            
            return Response(
                {"message": "초대를 수락했습니다.", "invitation": InvitationSerializer(invitation).data},
                status=status.HTTP_200_OK
            )
            
        except Invitation.DoesNotExist:
            return Response(
                {"error": "초대를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Accept invitation error: {str(e)}")
            return Response(
                {"error": "초대 수락 중 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DeclineInvitation(APIView):
    """Decline invitation endpoint - POST /api/invitations/{id}/decline/"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        try:
            invitation = Invitation.objects.get(
                pk=pk,
                recipient_email=request.user.email,
                status='pending'
            )
            
            if invitation.is_expired():
                return Response(
                    {"error": "초대가 만료되었습니다."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            invitation.status = 'declined'
            invitation.save()
            
            return Response(
                {"message": "초대를 거절했습니다.", "invitation": InvitationSerializer(invitation).data},
                status=status.HTTP_200_OK
            )
            
        except Invitation.DoesNotExist:
            return Response(
                {"error": "초대를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Decline invitation error: {str(e)}")
            return Response(
                {"error": "초대 거절 중 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SearchUserByEmail(APIView):
    """이메일로 사용자 검색"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        email = request.query_params.get('email')
        
        if not email:
            return Response(
                {"error": "이메일을 입력하세요."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email)
            avatar = None
            
            try:
                if hasattr(user, 'userprofile') and user.userprofile.profile_image:
                    avatar = user.userprofile.profile_image.url
            except:
                pass
            
            result = {
                'exists': True,
                'name': user.get_full_name() or user.username,
                'avatar': avatar
            }
        except User.DoesNotExist:
            result = {'exists': False}
        
        serializer = UserSearchSerializer(result)
        return Response(serializer.data)
