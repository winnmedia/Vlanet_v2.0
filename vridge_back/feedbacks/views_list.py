"""
  
"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import FeedBack as Feedback
from .serializers import FeedBackSerializer as FeedbackSerializer

class FeedbackListView(generics.ListAPIView):
    """
        ()
    """
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """
            
        """
        if self.request.user.is_authenticated:
            #     
            return Feedback.objects.filter(
                project__members=self.request.user
            ).select_related('project', 'user').distinct()
        else:
            #    
            return Feedback.objects.none()
    
    def list(self, request, *args, **kwargs):
        """
           200 
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': len(serializer.data),
            'results': serializer.data
        })