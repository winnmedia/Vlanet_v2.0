from django.urls import path
from . import views

app_name = 'calendars'

urlpatterns = [
    # 일정 목록/생성 - GET/POST /api/calendar/events/
    path('events/', views.CalendarEventList.as_view(), name='event-list'),
    
    # 일정 상세/수정/삭제 - GET/PUT/DELETE /api/calendar/events/{id}/
    path('events/<int:pk>/', views.CalendarEventDetail.as_view(), name='event-detail'),
    
    # 월별 일정 조회 - GET /api/calendar/month/{year}/{month}/
    path('month/<int:year>/<int:month>/', views.CalendarMonthView.as_view(), name='month-view'),
    
    # 실시간 업데이트 (polling) - GET /api/calendar/updates/
    path('updates/', views.CalendarEventUpdates.as_view(), name='event-updates'),
    
    # 일괄 업데이트 - POST /api/calendar/batch-update/
    path('batch-update/', views.CalendarEventBatchUpdate.as_view(), name='event-batch-update'),
    
    # 레거시 지원: 루트 경로도 events와 동일하게 처리
    path('', views.CalendarEventList.as_view(), name='legacy-event-list'),
]