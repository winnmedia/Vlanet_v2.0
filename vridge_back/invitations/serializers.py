from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Invitation, TeamMember, Friend

User = get_user_model()


class InvitationSerializer(serializers.ModelSerializer):
    """초대 시리얼라이저"""
    sender_email = serializers.EmailField(source='sender.email', read_only=True)
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    project_title = serializers.CharField(source='project.title', read_only=True, allow_null=True)
    
    class Meta:
        model = Invitation
        fields = [
            'id', 'sender', 'sender_email', 'sender_name',
            'recipient_email', 'project', 'project_title',
            'status', 'message', 'token', 'created_at',
            'updated_at', 'expires_at'
        ]
        read_only_fields = [
            'id', 'sender', 'sender_email', 'sender_name',
            'token', 'created_at', 'updated_at'
        ]
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['sender'] = request.user
        return super().create(validated_data)


class SendInvitationSerializer(serializers.Serializer):
    """초대 발송 시리얼라이저"""
    recipient_email = serializers.EmailField()
    project_id = serializers.IntegerField(required=False, allow_null=True)
    message = serializers.CharField(required=False, allow_blank=True)


class UpdateInvitationSerializer(serializers.Serializer):
    """초대 응답 시리얼라이저"""
    status = serializers.ChoiceField(choices=['accepted', 'declined'])
    message = serializers.CharField(required=False, allow_blank=True)


class TeamMemberSerializer(serializers.ModelSerializer):
    """팀 멤버 시리얼라이저"""
    email = serializers.EmailField(source='user.email', read_only=True)
    name = serializers.CharField(source='user.get_full_name', read_only=True)
    avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = TeamMember
        fields = [
            'id', 'user', 'email', 'name', 'avatar',
            'project', 'role', 'status', 'joined_at', 'last_active'
        ]
        read_only_fields = ['id', 'joined_at', 'last_active']
    
    def get_avatar(self, obj):
        # 프로필 이미지가 있다면 반환
        try:
            if hasattr(obj.user, 'userprofile') and obj.user.userprofile.profile_image:
                return obj.user.userprofile.profile_image.url
        except:
            pass
        return None


class FriendSerializer(serializers.ModelSerializer):
    """친구 시리얼라이저"""
    email = serializers.EmailField(source='friend.email', read_only=True)
    name = serializers.CharField(source='friend.get_full_name', read_only=True)
    avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = Friend
        fields = [
            'id', 'friend', 'email', 'name', 'avatar',
            'added_at', 'last_interaction', 'projects_shared'
        ]
        read_only_fields = ['id', 'added_at', 'last_interaction']
    
    def get_avatar(self, obj):
        try:
            if hasattr(obj.friend, 'userprofile') and obj.friend.userprofile.profile_image:
                return obj.friend.userprofile.profile_image.url
        except:
            pass
        return None


class InvitationStatsSerializer(serializers.Serializer):
    """초대 통계 시리얼라이저"""
    total_sent = serializers.IntegerField()
    total_received = serializers.IntegerField()
    pending_sent = serializers.IntegerField()
    pending_received = serializers.IntegerField()
    accepted_sent = serializers.IntegerField()
    accepted_received = serializers.IntegerField()
    declined_sent = serializers.IntegerField()
    declined_received = serializers.IntegerField()


class UserSearchSerializer(serializers.Serializer):
    """사용자 검색 결과 시리얼라이저"""
    exists = serializers.BooleanField()
    name = serializers.CharField(required=False)
    avatar = serializers.CharField(required=False)