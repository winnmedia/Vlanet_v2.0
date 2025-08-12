from django.urls import path
from . import views
from . import views_api  # Import enhanced API views
from .create_users_endpoint import CreateTestUsers
from rest_framework_simplejwt.views import TokenRefreshView
#     
# from . import views_signup_with_email
# from . import views_profile
from . import views_mypage
from . import views_profile_upload
from . import views_email_monitor
from . import views_account_management

# Import api_urls patterns safely
try:
    from .api_urls import urlpatterns as api_patterns
except ImportError:
    api_patterns = []

urlpatterns = api_patterns + [
    # Enhanced API endpoints with improved error handling and CORS
    path("login/", views_api.LoginAPIView.as_view(), name='login'),
    path("signup/", views_api.SignupAPIView.as_view(), name='signup'),
    path("me/", views_api.UserMeAPIView.as_view(), name='user_me'),
    path("refresh/", TokenRefreshView.as_view(), name='token_refresh'),  # JWT refresh
    
    # Legacy endpoints (fallback)
    path("login-legacy/", views.SignIn.as_view(), name='login_legacy'),
    path("signup-legacy/", views.SignUp.as_view(), name='signup_legacy'),
    
    #      ( )
    # path("signup/request/", views_signup_with_email.SignUpRequest.as_view()),  # Step 1:   
    # path("signup/verify/", views_signup_with_email.SignUpVerify.as_view()),     # Step 2:  
    # path("signup/complete/", views_signup_with_email.SignUpComplete.as_view()),  # Step 3:  
    
    # Enhanced validation endpoints
    path("check-email/", views_api.CheckEmailAPIView.as_view(), name='check_email'),
    path("check-nickname/", views_api.CheckNicknameAPIView.as_view(), name='check_nickname'),
    
    # Legacy validation endpoints (fallback)
    path("check-email-legacy/", views.CheckEmail.as_view()),
    path("check-nickname-legacy/", views.CheckNickname.as_view()),
    path("send-authnumber/<str:types>/", views.SendAuthNumber.as_view()),  #   ()
    path("signup-emailauth/<str:types>/", views.EmailAuth.as_view()),  #   ()
    path("password-reset/", views.ResetPassword.as_view()),
    path("login/kakao/", views.KakaoLogin.as_view()),
    path("login/naver/", views.NaverLogin.as_view()),
    path("login/google/", views.GoogleLogin.as_view()),
    path("memo/", views.UserMemo.as_view()),  # create memo
    path("memo/<int:id>/", views.UserMemo.as_view()),  # delete memo
    path("create-test-users/", CreateTestUsers.as_view()),  #   
    
    #   URL ( )
    # path("profile/", views_profile.UserProfile.as_view()),  #  /
    # path("profile/change-password/", views_profile.ChangePassword.as_view()),  #  
    # path("profile/stats/", views_profile.UserStats.as_view()),  #  
    # path("profile/delete-account/", views_profile.DeleteAccount.as_view()),  #  
    
    #   URL
    path("mypage/", views_mypage.MyPageView.as_view()),  #   
    path("mypage/activity/", views_mypage.UserActivityView.as_view()),  #  
    path("mypage/preferences/", views_mypage.UserPreferencesView.as_view()),  #  
    
    #    URL
    path("profile/upload-image/", views_profile_upload.ProfileImageUpload.as_view()),  #   /
    path("profile/update/", views_profile_upload.ProfileUpdate.as_view()),  #   
    
    #   URL
    path("notifications/", views.NotificationView.as_view()),  #   / 
    path("notifications/unread-count/", views.UnreadNotificationCount.as_view()),  #    
    path("notifications/mark-read/", views.MarkNotificationsRead.as_view()),  #    
    path("notifications/<int:notification_id>/", views.NotificationDetail.as_view()),  #  
    
    #   URL
    path("friends/", views.FriendshipView.as_view()),  #   / / 
    path("friends/requests/", views.FriendRequestView.as_view()),  #    
    path("friends/<int:friendship_id>/response/", views.FriendRequestResponse.as_view()),  #   /
    path("friends/search/", views.FriendSearch.as_view()),  #  
    path("friends/block/", views.FriendBlockView.as_view()),  #  / 
    
    #    URL
    path("recent-invitations/", views.RecentInvitationsView.as_view()),  #    
    
    #    URL
    path("verify-email/<str:token>/", views.EmailVerificationView.as_view()),  #   
    path("resend-verification-email/", views.ResendVerificationEmailView.as_view()),  #   
    path("check-verification-status/", views.CheckEmailVerificationStatusView.as_view()),  #   
    
    #  URL ()
    path("debug/jwt/", views.JWTDebugView.as_view()),  # JWT  
    path("debug/auth/", views.AuthDebugView.as_view()),  #   
    
    #   URL ()
    path("email-monitor/status/<str:email_id>/", views_email_monitor.EmailStatusView.as_view()),  #   
    path("email-monitor/dashboard/", views_email_monitor.EmailMonitorDashboardView.as_view()),  #  
    path("email-monitor/resend/<str:email_id>/", views_email_monitor.EmailResendView.as_view()),  #  
    path("email-monitor/bulk-send/", views_email_monitor.BulkEmailView.as_view()),  #   
    path("email-monitor/cleanup/", views_email_monitor.EmailCleanupView.as_view()),  #   
    
    #   URL (   )
    path("account/verify-email/request/", views_account_management.EmailVerificationRequestView.as_view()),  #   
    path("account/verify-email/confirm/", views_account_management.EmailVerificationConfirmView.as_view()),  #   
    path("account/find-username/", views_account_management.FindUsernameView.as_view()),  # ID 
    path("account/password-reset/request/", views_account_management.PasswordResetRequestView.as_view()),  #   
    path("account/password-reset/confirm/", views_account_management.PasswordResetConfirmView.as_view()),  #   
    path("account/delete/", views_account_management.AccountDeletionView.as_view()),  #  
    path("account/recover/", views_account_management.AccountRecoveryView.as_view()),  #  
    path("account/status/", views_account_management.AccountStatusView.as_view()),  #   
]
