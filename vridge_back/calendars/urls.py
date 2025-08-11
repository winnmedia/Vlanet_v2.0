from django.urls import path
from . import views

app_name = 'calendars'

urlpatterns = [
    # 캘린더 이벤트 목록 및 생성
    path('', views.CalendarEventList.as_view(), name='event-list'),
    
    # 캘린더 이벤트 상세 조회, 수정, 삭제
    path('<int:pk>/', views.CalendarEventDetail.as_view(), name='event-detail'),
    
    # 캘린더 업데이트 확인 (polling)
    path('updates/', views.CalendarEventUpdates.as_view(), name='event-updates'),
    
    # 캘린더 일괄 업데이트
    path('batch-update/', views.CalendarEventBatchUpdate.as_view(), name='event-batch-update'),
]