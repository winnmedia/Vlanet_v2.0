from rest_framework import serializers
from .models import CalendarEvent


class CalendarEventSerializer(serializers.ModelSerializer):
    """  """
    
    class Meta:
        model = CalendarEvent
        fields = [
            'id', 'title', 'description', 'date', 'time',
            'user', 'project', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        #    
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)


class CalendarEventListSerializer(serializers.ModelSerializer):
    """    ( )"""
    
    class Meta:
        model = CalendarEvent
        fields = [
            'id', 'title', 'date', 'time', 'project'
        ]


class CalendarUpdateEventSerializer(serializers.Serializer):
    """   """
    type = serializers.ChoiceField(choices=['create', 'update', 'delete', 'bulk_update'])
    event = CalendarEventSerializer(required=False)
    eventId = serializers.IntegerField(required=False)
    events = CalendarEventSerializer(many=True, required=False)
    timestamp = serializers.DateTimeField()