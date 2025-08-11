"""
  API 
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from .email_monitor import email_monitor
from .email_queue import email_queue_manager
import logging

logger = logging.getLogger(__name__)


class EmailStatusView(APIView):
    """   """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, email_id):
        """  """
        try:
            #   
            email_status = email_monitor.get_email_status(email_id)
            
            if not email_status:
                return Response({
                    "message": "   ."
                }, status=status.HTTP_404_NOT_FOUND)
            
            #    (     )
            if not request.user.is_staff:
                if email_status.get('recipient') != request.user.email:
                    return Response({
                        "message": " ."
                    }, status=status.HTTP_403_FORBIDDEN)
            
            return Response({
                "status": "success",
                "data": email_status
            })
            
        except Exception as e:
            logger.error(f"   : {str(e)}")
            return Response({
                "message": "     ."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmailMonitorDashboardView(APIView):
    """   ()"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        """      """
        try:
            #   
            hours = int(request.GET.get('hours', 24))
            limit = int(request.GET.get('limit', 50))
            email_type = request.GET.get('type', None)
            
            #  
            statistics = email_monitor.get_statistics(hours=hours)
            
            #   
            recent_emails = email_monitor.get_recent_emails(limit=limit, email_type=email_type)
            
            #  
            queue_size = email_queue_manager.queue.qsize() if hasattr(email_queue_manager.queue, 'qsize') else 0
            
            return Response({
                "status": "success",
                "data": {
                    "statistics": statistics,
                    "recent_emails": recent_emails,
                    "queue_status": {
                        "size": queue_size,
                        "is_running": email_queue_manager.is_running,
                        "batch_size": email_queue_manager.batch_size,
                        "pending_batch_count": len(email_queue_manager.pending_batch)
                    }
                }
            })
            
        except Exception as e:
            logger.error(f"   : {str(e)}")
            return Response({
                "message": "     ."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmailResendView(APIView):
    """ """
    permission_classes = [IsAdminUser]
    
    def post(self, request, email_id):
        """  """
        try:
            #   
            email_status = email_monitor.get_email_status(email_id)
            
            if not email_status:
                return Response({
                    "message": "   ."
                }, status=status.HTTP_404_NOT_FOUND)
            
            #    
            if email_status.get('status') not in ['failed', 'bounced']:
                return Response({
                    "message": "    ."
                }, status=status.HTTP_400_BAD_REQUEST)
            
            #   
            new_email_id = email_queue_manager.add_email(
                subject=email_status.get('subject'),
                body=email_status.get('body', ''),
                recipient_list=[email_status.get('recipient')],
                html_message=email_status.get('html_message'),
                priority=1,  #  
                email_type=email_status.get('type', 'general')
            )
            
            return Response({
                "status": "success",
                "message": "   .",
                "data": {
                    "new_email_id": new_email_id
                }
            })
            
        except Exception as e:
            logger.error(f"  : {str(e)}")
            return Response({
                "message": "    ."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BulkEmailView(APIView):
    """  """
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        """   """
        try:
            email_list = request.data.get('emails', [])
            
            if not email_list:
                return Response({
                    "message": "   ."
                }, status=status.HTTP_400_BAD_REQUEST)
            
            #  
            for email in email_list:
                if not email.get('subject') or not email.get('recipient_list'):
                    return Response({
                        "message": "  subject recipient_list ."
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            #   
            email_ids = email_queue_manager.add_bulk_emails(email_list)
            
            return Response({
                "status": "success",
                "message": f"{len(email_ids)}    .",
                "data": {
                    "email_ids": email_ids,
                    "count": len(email_ids)
                }
            })
            
        except Exception as e:
            logger.error(f"   : {str(e)}")
            return Response({
                "message": "     ."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmailCleanupView(APIView):
    """   """
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        """  """
        try:
            days = int(request.data.get('days', 7))
            
            if days < 1:
                return Response({
                    "message": "  1  ."
                }, status=status.HTTP_400_BAD_REQUEST)
            
            #  
            deleted_count = email_monitor.cleanup_old_records(days=days)
            
            return Response({
                "status": "success",
                "message": f"{deleted_count}    .",
                "data": {
                    "deleted_count": deleted_count,
                    "days": days
                }
            })
            
        except Exception as e:
            logger.error(f"   : {str(e)}")
            return Response({
                "message": "     ."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)