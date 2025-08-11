from .api_urls import urlpatterns as api_patterns

from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = api_patterns + [
    #     
    path('<int:project_id>/documents/', views.DocumentListView.as_view(), name='document-list'),
    path('<int:project_id>/documents/upload/', views.DocumentListView.as_view(), name='document-upload'),
    
    #   , , 
    path('<int:project_id>/documents/<int:document_id>/', views.DocumentDetailView.as_view(), name='document-detail'),
    path('<int:project_id>/documents/<int:document_id>/download/', views.DocumentDetailView.as_view(), name='document-download'),
]