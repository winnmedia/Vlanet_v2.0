"""
   
"""

from rest_framework import serializers


class ProposalExportSerializer(serializers.Serializer):
    """   """
    
    planning_text = serializers.CharField(
        max_length=10000,
        help_text="    ( 10,000)"
    )
    
    #  
    title = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        help_text="  ()"
    )
    
    project_type = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        help_text="  ()"
    )
    
    export_format = serializers.ChoiceField(
        choices=[
            ('google_slides', 'Google Slides'),
            ('json', 'JSON '),
            ('both', ' ')
        ],
        default='google_slides',
        help_text=" "
    )
    
    def validate_planning_text(self, value):
        """  """
        if not value or not value.strip():
            raise serializers.ValidationError("  .")
        
        if len(value.strip()) < 50:
            raise serializers.ValidationError("   .  50  .")
        
        return value.strip()


class ProposalExportResponseSerializer(serializers.Serializer):
    """   """
    
    success = serializers.BooleanField()
    message = serializers.CharField(max_length=500)
    
    #   
    structured_data = serializers.JSONField(required=False)
    presentation = serializers.JSONField(required=False)
    
    #   
    error = serializers.CharField(max_length=500, required=False)
    step = serializers.CharField(max_length=50, required=False)
    details = serializers.JSONField(required=False)


class ProposalStructurePreviewSerializer(serializers.Serializer):
    """   """
    
    planning_text = serializers.CharField(
        max_length=10000,
        help_text="  "
    )
    
    preview_only = serializers.BooleanField(
        default=True,
        help_text="  (Google Slides  )"
    )


class SlideContentSerializer(serializers.Serializer):
    """  """
    
    title_text = serializers.CharField(max_length=100, required=False)
    subtitle_text = serializers.CharField(max_length=200, required=False)
    bullet_points = serializers.ListField(
        child=serializers.CharField(max_length=200),
        required=False
    )
    left_column = serializers.ListField(
        child=serializers.CharField(max_length=200),
        required=False
    )
    right_column = serializers.ListField(
        child=serializers.CharField(max_length=200),
        required=False
    )
    budget_breakdown = serializers.ListField(
        child=serializers.CharField(max_length=200),
        required=False
    )
    timeline = serializers.ListField(
        child=serializers.CharField(max_length=200),
        required=False
    )


class SlideInfoSerializer(serializers.Serializer):
    """  """
    
    slide_number = serializers.IntegerField()
    layout = serializers.ChoiceField(choices=[
        ('TITLE', 'Title'),
        ('TITLE_AND_BODY', 'Title and Body'),
        ('TITLE_AND_TWO_COLUMNS', 'Title and Two Columns'),
        ('CAPTION_ONLY', 'Caption Only')
    ])
    title = serializers.CharField(max_length=100)
    content = SlideContentSerializer()


class ProposalMetadataSerializer(serializers.Serializer):
    """  """
    
    title = serializers.CharField(max_length=100)
    subtitle = serializers.CharField(max_length=200, required=False)
    project_type = serializers.CharField(max_length=50)
    target_audience = serializers.CharField(max_length=100)
    duration = serializers.CharField(max_length=50)
    budget_range = serializers.CharField(max_length=100, required=False)
    deadline = serializers.CharField(max_length=100, required=False)


class StructuredProposalSerializer(serializers.Serializer):
    """  """
    
    metadata = ProposalMetadataSerializer()
    slides = serializers.ListField(child=SlideInfoSerializer())
    
    def validate_slides(self, value):
        """  """
        if len(value) < 3:
            raise serializers.ValidationError(" 3   .")
        
        if len(value) > 15:
            raise serializers.ValidationError("  15 .")
        
        return value