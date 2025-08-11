from django.urls import path
from . import views

urlpatterns = [
    # Standard REST API patterns
    path('', views.ReceivedInvitations.as_view(), name='invitation-list'),  # GET /api/invitations/
    path('', views.SendInvitation.as_view(), name='invitation-create'),  # POST /api/invitations/
    path('<int:pk>/', views.InvitationDetail.as_view(), name='invitation-detail'),  # GET /api/invitations/{id}/
    path('<int:pk>/', views.RespondToInvitation.as_view(), name='invitation-update'),  # PUT/PATCH /api/invitations/{id}/
    path('<int:pk>/cancel/', views.CancelInvitation.as_view(), name='invitation-delete'),  # DELETE /api/invitations/{id}/cancel/
    
    # Accept/Decline endpoints
    path('<int:pk>/accept/', views.AcceptInvitation.as_view(), name='invitation-accept'),  # POST /api/invitations/{id}/accept/
    path('<int:pk>/decline/', views.DeclineInvitation.as_view(), name='invitation-decline'),  # POST /api/invitations/{id}/decline/
    
    # Additional endpoints
    path('send/', views.SendInvitation.as_view(), name='send-invitation'),  # Legacy support
    path('received/', views.ReceivedInvitations.as_view(), name='received-invitations'),
    path('sent/', views.SentInvitations.as_view(), name='sent-invitations'),
    path('<int:pk>/respond/', views.RespondToInvitation.as_view(), name='respond-invitation'),
    path('<int:pk>/resend/', views.ResendInvitation.as_view(), name='resend-invitation'),
    
    # Team management
    path('team-members/', views.TeamMemberList.as_view(), name='team-member-list'),
    path('team-members/<int:pk>/remove/', views.RemoveTeamMember.as_view(), name='remove-team-member'),
    
    # Friends management
    path('friends/', views.FriendList.as_view(), name='friend-list'),
    path('friends/<int:pk>/remove/', views.RemoveFriend.as_view(), name='remove-friend'),
    
    # Utility endpoints
    path('stats/', views.InvitationStats.as_view(), name='invitation-stats'),
    path('search-user/', views.SearchUserByEmail.as_view(), name='search-user'),
]