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
    """     """
    serializer_class = CalendarEventSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = CalendarEvent.objects.filter(user=self.request.user)
        
        #  
        date = self.request.query_params.get('date')
        if date:
            try:
                date_obj = datetime.strptime(date, '%Y-%m-%d').date()
                queryset = queryset.filter(date=date_obj)
            except ValueError:
                pass
        
        #   
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__range=[start, end])
            except ValueError:
                pass
        
        #  
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
                {"error": "처리 중 오류가 발생했습니다."},
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
                {"error": "처리 중 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CalendarEventDetail(generics.RetrieveUpdateDestroyAPIView):
    """   , , """
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
                {"error": "처리 중 오류가 발생했습니다."},
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
                {"error": "처리 중 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CalendarEventUpdates(APIView):
    """   (polling)"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # since     
            since = request.query_params.get('since')
            updates = []
            
            if since:
                try:
                    since_datetime = datetime.fromisoformat(since.replace('Z', '+00:00'))
                    #      
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
            
            #   
            latest_timestamp = timezone.now().isoformat()
            
            return Response({
                'updates': updates,
                'latest_timestamp': latest_timestamp
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Calendar updates error: {str(e)}")
            return Response(
                {"error": "처리 중 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CalendarEventBatchUpdate(APIView):
    """일괄 업데이트"""
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
                {"error": "일괄 업데이트 중 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CalendarMonthView(APIView):
    """월별 일정 조회 - GET /api/calendar/month/{year}/{month}/"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, year, month):
        try:
            # 년월 유효성 검증
            if not (1 <= month <= 12):
                return Response(
                    {"error": "유효하지 않은 월입니다. (1-12)"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not (1900 <= year <= 2100):
                return Response(
                    {"error": "유효하지 않은 년도입니다."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 해당 월의 시작일과 끝일 계산
            import calendar
            _, last_day = calendar.monthrange(year, month)
            start_date = datetime(year, month, 1).date()
            end_date = datetime(year, month, last_day).date()
            
            # 해당 월의 일정 조회
            events = CalendarEvent.objects.filter(
                user=request.user,
                date__range=[start_date, end_date]
            ).select_related('project').order_by('date', 'time')
            
            # 일자별로 그룹화
            events_by_date = {}
            for event in events:
                date_key = event.date.strftime('%Y-%m-%d')
                if date_key not in events_by_date:
                    events_by_date[date_key] = []
                events_by_date[date_key].append(CalendarEventSerializer(event).data)
            
            return Response({
                'year': year,
                'month': month,
                'events_by_date': events_by_date,
                'total_events': events.count(),
                'date_range': {
                    'start': start_date.strftime('%Y-%m-%d'),
                    'end': end_date.strftime('%Y-%m-%d')
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Calendar month view error: {str(e)}")
            return Response(
                {"error": "월별 일정 조회 중 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
