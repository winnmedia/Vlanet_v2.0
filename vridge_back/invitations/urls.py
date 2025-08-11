from django.urls import path
from . import views

urlpatterns = [
    # 초대 관리
    path('', views.InvitationListCreateView.as_view(), name='invitation-list-create'),
    path('<int:pk>/', views.InvitationDetailView.as_view(), name='invitation-detail'),
    
    # 받은 초대
    path('received/', views.ReceivedInvitationsView.as_view(), name='received-invitations'),
    
    # 초대 응답
    path('<int:pk>/accept/', views.AcceptInvitationView.as_view(), name='accept-invitation'),
    path('<int:pk>/reject/', views.RejectInvitationView.as_view(), name='reject-invitation'),
    
    # 초대 재발송
    path('<int:pk>/resend/', views.ResendInvitationView.as_view(), name='resend-invitation'),
    
    # 최근 초대한 사용자 목록
    path('recent-users/', views.RecentInvitedUsersView.as_view(), name='recent-invited-users'),
]