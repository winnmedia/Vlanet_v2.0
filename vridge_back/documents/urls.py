from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from . import views

app_name = 'documents'

# API endpoints
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def document_list_api(request):
    """문서 목록 API"""
    return Response({"documents": [], "count": 0})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def document_upload_api(request):
    """문서 업로드 API"""
    return Response({"message": "Upload endpoint ready", "status": "ok"})

urlpatterns = [
    # API patterns
    path('', document_list_api, name='document_list_api'),
    path('upload/', document_upload_api, name='document_upload_api'),
    
    # View patterns
    path('<int:project_id>/documents/', views.DocumentListView.as_view(), name='document-list'),
    path('<int:project_id>/documents/upload/', views.DocumentListView.as_view(), name='document-upload'),
    path('<int:project_id>/documents/<int:document_id>/', views.DocumentDetailView.as_view(), name='document-detail'),
    path('<int:project_id>/documents/<int:document_id>/download/', views.DocumentDetailView.as_view(), name='document-download'),
]