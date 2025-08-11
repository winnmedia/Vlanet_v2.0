from django.urls import path
from . import views
#     
# from . import views_improved
# from . import views_fixed
# from . import views_safe
# from . import views_idempotent
# from . import views_idempotent_fixed
# from . import views_ultra_safe
# from . import views_idempotent_final
# from . import views_atomic
# from . import views_fixed_final
# from . import views_column_safe

app_name = "projects"

urlpatterns = [
    path("", views.ProjectList.as_view()),  # GET /api/projects/
    path("project_list/", views.ProjectList.as_view()),  #   
    path(
        "invite_project/<int:project_id>", views.InviteMember.as_view()
    ),  #  ,  
    path(
        "invite/<str:uid>/<str:token>/", views.LegacyInviteRedirect.as_view(), name="legacy_invite"
    ),  #  
    #   -   
    path("create/", views.CreateProject.as_view()),  #   
    
    #   
    # path("create_fixed/", views_fixed_final.CreateProjectFixedFinal.as_view()),  #   
    # path("atomic-create/", views_atomic.AtomicProjectCreate.as_view()),  #   ()
    # path("create_idempotent", views_idempotent_final.CreateProjectIdempotentFinal.as_view()),  #    ()
    # path("create_safe", views_safe.CreateProjectSafe.as_view()),  # FeedBack   
    # path("create_ultra_safe", views_ultra_safe.CreateProjectUltraSafe.as_view()),  #   
    # path("create_improved", views_improved.CreateProjectImproved.as_view()),
    # path("debug_info", views_improved.ProjectDebugInfo.as_view()),
    
    path(
        "detail/<int:project_id>/", views.ProjectDetail.as_view()
    ),  # get,update, delete
    path("file/delete/<int:file_id>", views.ProjectFile.as_view()),
    path("memo/<int:id>", views.ProjectMemo.as_view()),  #  
    path("date_update/<int:id>", views.ProjectDate.as_view()),  #  
    
    #     
    path("<int:project_id>/feedback/", views.ProjectFeedback.as_view()),  #   /
    path("<int:project_id>/feedback/comments/", views.ProjectFeedbackComments.as_view()),  #   /
    path("<int:project_id>/feedback/upload/", views.ProjectFeedbackUpload.as_view()),  #   
    path("<int:project_id>/feedback/encoding-status/", views.ProjectFeedbackEncodingStatus.as_view()),  #   
    
    #   
    path("<int:project_id>/invitations/", views.ProjectInvitation.as_view()),  #   /
    path("invitations/", views.ProjectInvitation.as_view()),  #    
    path("invitations/token/<str:token>/", views.InvitationToken.as_view()),  #    
    path("invitations/<int:invitation_id>/response/", views.InvitationResponse.as_view()),  #  /
    
    #    
    path("frameworks/", views.DevelopmentFrameworkList.as_view()),  #   /
    path("frameworks/<int:framework_id>/", views.DevelopmentFrameworkDetail.as_view()),  #  //
    path("frameworks/<int:framework_id>/set-default/", views.SetDefaultFramework.as_view()),  #   
]
