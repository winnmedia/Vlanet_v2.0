from rest_framework import serializers
from .models import VideoAnalysisResult, AIFeedbackItem, AIAnalysisSettings


class AIFeedbackItemSerializer(serializers.ModelSerializer):
    """AI   """
    
    class Meta:
        model = AIFeedbackItem
        fields = [
            'id',
            'category',
            'severity',
            'title',
            'description',
            'feedback_type',
            'score',
            'message',
            'timestamp',
            'confidence_score',
            'metadata',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class VideoAnalysisResultSerializer(serializers.ModelSerializer):
    """   """
    
    feedback_items = AIFeedbackItemSerializer(many=True, read_only=True)
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    feedback_id = serializers.IntegerField(source='feedback.id', read_only=True)
    
    class Meta:
        model = VideoAnalysisResult
        fields = [
            'id',
            'feedback',
            'feedback_id',
            'status',
            'overall_score',
            'analysis_data',
            'error_message',
            'processing_time',
            'ai_model_version',
            'ai_server_used',
            'external_video_id',
            'analysis_type',
            'created_by',
            'created_by_email',
            'processing_started_at',
            'processing_completed_at',
            'created_at',
            'updated_at',
            'feedback_items'
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'feedback_items',
            'created_by_email',
            'feedback_id'
        ]


class VideoAnalysisCreateSerializer(serializers.Serializer):
    """   """
    
    feedback_id = serializers.IntegerField(required=True)
    analysis_type = serializers.ChoiceField(
        choices=['internal', 'twelve_labs', 'custom'],
        default='twelve_labs'
    )
    options = serializers.JSONField(required=False, default=dict)
    
    def validate_feedback_id(self, value):
        from feedbacks.models import FeedBack
        try:
            FeedBack.objects.get(id=value)
        except FeedBack.DoesNotExist:
            raise serializers.ValidationError("   ID.")
        return value


class VideoSearchSerializer(serializers.Serializer):
    """  """
    
    query = serializers.CharField(required=True, min_length=1, max_length=500)
    options = serializers.ListField(
        child=serializers.ChoiceField(choices=['visual', 'conversation', 'text_in_video', 'logo']),
        default=['visual', 'conversation', 'text_in_video']
    )
    limit = serializers.IntegerField(default=10, min_value=1, max_value=100)
    
    def validate_query(self, value):
        #  
        value = value.strip()
        if not value:
            raise serializers.ValidationError(" .")
        return value


class AIAnalysisSettingsSerializer(serializers.ModelSerializer):
    """AI   """
    
    class Meta:
        model = AIAnalysisSettings
        fields = [
            'is_enabled',
            'ai_server_url',
            'ai_server_api_key',
            'analyze_composition',
            'analyze_lighting',
            'analyze_audio',
            'analyze_stability',
            'analyze_color',
            'analyze_motion',
            'max_video_duration',
            'analysis_timeout',
            'updated_at'
        ]
        read_only_fields = ['updated_at']
        extra_kwargs = {
            'ai_server_api_key': {'write_only': True}
        }