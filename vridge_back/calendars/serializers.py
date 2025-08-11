from rest_framework import serializers
from .models import CalendarEvent


class CalendarEventSerializer(serializers.ModelSerializer):
    """캘린더 이벤트 시리얼라이저"""
    
    class Meta:
        model = CalendarEvent
        fields = [
            'id', 'title', 'description', 'date', 'time',
            'user', 'project', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        # 자동으로 현재 사용자 설정
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)


class CalendarEventListSerializer(serializers.ModelSerializer):
    """캘린더 이벤트 목록 시리얼라이저 (간단한 정보만)"""
    
    class Meta:
        model = CalendarEvent
        fields = [
            'id', 'title', 'date', 'time', 'project'
        ]


class CalendarUpdateEventSerializer(serializers.Serializer):
    """캘린더 업데이트 이벤트 시리얼라이저"""
    type = serializers.ChoiceField(choices=['create', 'update', 'delete', 'bulk_update'])
    event = CalendarEventSerializer(required=False)
    eventId = serializers.IntegerField(required=False)
    events = CalendarEventSerializer(many=True, required=False)
    timestamp = serializers.DateTimeField()