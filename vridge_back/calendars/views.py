from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import CalendarEvent
from .serializers import CalendarEventSerializer, CalendarEventListSerializer, CalendarUpdateEventSerializer
import logging

logger = logging.getLogger(__name__)


class CalendarEventList(generics.ListCreateAPIView):
    """캘린더 이벤트 목록 조회 및 생성"""
    serializer_class = CalendarEventSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = CalendarEvent.objects.filter(user=self.request.user)
        
        # 날짜 필터링
        date = self.request.query_params.get('date')
        if date:
            try:
                date_obj = datetime.strptime(date, '%Y-%m-%d').date()
                queryset = queryset.filter(date=date_obj)
            except ValueError:
                pass
        
        # 날짜 범위 필터링
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__range=[start, end])
            except ValueError:
                pass
        
        # 프로젝트 필터링
        project_id = self.request.query_params.get('project_id')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        return queryset.select_related('project')
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Calendar list error: {str(e)}")
            return Response(
                {"error": "캘린더 이벤트 조회 중 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Calendar create error: {str(e)}")
            return Response(
                {"error": "캘린더 이벤트 생성 중 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CalendarEventDetail(generics.RetrieveUpdateDestroyAPIView):
    """캘린더 이벤트 상세 조회, 수정, 삭제"""
    serializer_class = CalendarEventSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'
    
    def get_queryset(self):
        return CalendarEvent.objects.filter(user=self.request.user)
    
    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Calendar update error: {str(e)}")
            return Response(
                {"error": "캘린더 이벤트 수정 중 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"Calendar delete error: {str(e)}")
            return Response(
                {"error": "캘린더 이벤트 삭제 중 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CalendarEventUpdates(APIView):
    """캘린더 업데이트 확인 (polling용)"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # since 파라미터로 마지막 동기화 시간 받기
            since = request.query_params.get('since')
            updates = []
            
            if since:
                try:
                    since_datetime = datetime.fromisoformat(since.replace('Z', '+00:00'))
                    # 마지막 동기화 이후 변경된 이벤트 조회
                    events = CalendarEvent.objects.filter(
                        user=request.user,
                        updated_at__gt=since_datetime
                    ).select_related('project')
                    
                    for event in events:
                        update_event = {
                            'type': 'update',
                            'event': CalendarEventSerializer(event).data,
                            'timestamp': event.updated_at.isoformat()
                        }
                        updates.append(update_event)
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid since parameter: {since}, error: {e}")
            
            # 최신 타임스탬프 계산
            latest_timestamp = timezone.now().isoformat()
            
            return Response({
                'updates': updates,
                'latest_timestamp': latest_timestamp
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Calendar updates error: {str(e)}")
            return Response(
                {"error": "캘린더 업데이트 확인 중 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CalendarEventBatchUpdate(APIView):
    """캘린더 이벤트 일괄 업데이트"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            updates = request.data.get('updates', [])
            updated_events = []
            
            for update in updates:
                event_id = update.get('id')
                data = update.get('data', {})
                
                try:
                    event = CalendarEvent.objects.get(id=event_id, user=request.user)
                    serializer = CalendarEventSerializer(event, data=data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        updated_events.append(serializer.data)
                except CalendarEvent.DoesNotExist:
                    logger.warning(f"Calendar event {event_id} not found for batch update")
                    continue
            
            return Response(updated_events, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Calendar batch update error: {str(e)}")
            return Response(
                {"error": "캘린더 일괄 업데이트 중 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
