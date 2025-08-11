from django.http import JsonResponse, FileResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import transaction
from users.utils import user_validator
from projects.models import Project
from .models import Document
import json
import logging
import os

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class DocumentListView(View):
    """    """
    
    @user_validator
    def get(self, request, project_id):
        """   """
        try:
            user = request.user
            
            #   
            try:
                project = Project.objects.get(id=project_id)
            except Project.DoesNotExist:
                return JsonResponse({'message': '   .'}, status=404)
            
            #  
            is_member = project.members.filter(user=user).exists()
            if project.user != user and not is_member:
                return JsonResponse({'message': ' .'}, status=403)
            
            #   
            documents = Document.objects.filter(
                project=project,
                is_active=True
            ).select_related('uploader')
            
            document_list = []
            for doc in documents:
                document_list.append({
                    'id': doc.id,
                    'filename': doc.filename,
                    'category': doc.category,
                    'description': doc.description,
                    'size': doc.size,
                    'mime_type': doc.mime_type,
                    'uploaded_at': doc.uploaded_at.isoformat(),
                    'uploader': {
                        'id': doc.uploader.id if doc.uploader else None,
                        'username': doc.uploader.username if doc.uploader else 'Unknown'
                    },
                    'download_count': doc.download_count,
                    'url': doc.file.url if doc.file else None
                })
            
            return JsonResponse({
                'success': True,
                'documents': document_list
            })
            
        except Exception as e:
            logger.error(f"Document list error: {str(e)}", exc_info=True)
            return JsonResponse({'message': '     .'}, status=500)
    
    @user_validator
    @transaction.atomic
    def post(self, request, project_id):
        """ """
        try:
            user = request.user
            
            #   
            try:
                project = Project.objects.get(id=project_id)
            except Project.DoesNotExist:
                return JsonResponse({'message': '   .'}, status=404)
            
            #  
            is_member = project.members.filter(user=user).exists()
            if project.user != user and not is_member:
                return JsonResponse({'message': ' .'}, status=403)
            
            #  
            if 'file' not in request.FILES:
                return JsonResponse({'message': ' .'}, status=400)
            
            uploaded_file = request.FILES['file']
            category = request.POST.get('category', 'other')
            description = request.POST.get('description', '')
            
            #    (50MB)
            if uploaded_file.size > 50 * 1024 * 1024:
                return JsonResponse({'message': '  50MB   .'}, status=400)
            
            #   
            allowed_extensions = [
                '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
                '.txt', '.jpg', '.jpeg', '.png', '.gif', '.zip', '.rar'
            ]
            
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()
            if file_extension not in allowed_extensions:
                return JsonResponse({'message': '   .'}, status=400)
            
            #  
            document = Document.objects.create(
                project=project,
                uploader=user,
                filename=uploaded_file.name,
                file=uploaded_file,
                category=category,
                description=description,
                size=uploaded_file.size
            )
            
            logger.info(f"Document uploaded: {document.filename} by {user.username}")
            
            return JsonResponse({
                'success': True,
                'message': ' .',
                'document': {
                    'id': document.id,
                    'filename': document.filename,
                    'category': document.category,
                    'size': document.size
                }
            })
            
        except Exception as e:
            logger.error(f"Document upload error: {str(e)}", exc_info=True)
            return JsonResponse({'message': '    .'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class DocumentDetailView(View):
    """  , , """
    
    @user_validator
    def get(self, request, project_id, document_id):
        """ """
        try:
            user = request.user
            
            #  
            try:
                document = Document.objects.select_related('project').get(
                    id=document_id,
                    project_id=project_id,
                    is_active=True
                )
            except Document.DoesNotExist:
                return JsonResponse({'message': '   .'}, status=404)
            
            #  
            project = document.project
            is_member = project.members.filter(user=user).exists()
            if project.user != user and not is_member:
                return JsonResponse({'message': ' .'}, status=403)
            
            #   
            document.increment_download_count()
            
            #  
            if document.file:
                response = FileResponse(
                    document.file,
                    as_attachment=True,
                    filename=document.filename
                )
                return response
            else:
                return JsonResponse({'message': '   .'}, status=404)
                
        except Exception as e:
            logger.error(f"Document download error: {str(e)}", exc_info=True)
            return JsonResponse({'message': '    .'}, status=500)
    
    @user_validator
    def delete(self, request, project_id, document_id):
        """ """
        try:
            user = request.user
            
            #  
            try:
                document = Document.objects.select_related('project').get(
                    id=document_id,
                    project_id=project_id,
                    is_active=True
                )
            except Document.DoesNotExist:
                return JsonResponse({'message': '   .'}, status=404)
            
            #   (      )
            project = document.project
            if project.user != user and document.uploader != user:
                return JsonResponse({'message': ' .'}, status=403)
            
            #  
            document.is_active = False
            document.save()
            
            logger.info(f"Document deleted: {document.filename} by {user.username}")
            
            return JsonResponse({
                'success': True,
                'message': ' .'
            })
            
        except Exception as e:
            logger.error(f"Document delete error: {str(e)}", exc_info=True)
            return JsonResponse({'message': '    .'}, status=500)