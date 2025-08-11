from django.urls import path
from . import views

app_name = 'feedbacks'

urlpatterns = [
    #    ()
    path('', views.FeedbackListView.as_view(), name='feedback-list'),
    
    #     
    path('projects/<int:project_id>/feedbacks/', 
         views.ProjectFeedbackListView.as_view(), 
         name='project-feedbacks'),
    
    #   , , 
    path('feedbacks/<int:feedback_id>/', 
         views.FeedbackDetailView.as_view(), 
         name='feedback-detail'),
    
    #   
    path('feedbacks/<int:feedback_id>/messages/', 
         views.FeedbackMessageView.as_view(), 
         name='feedback-messages'),
    
    #   
    path('projects/<int:project_id>/feedbacks/<int:feedback_id>/comments/', 
         views.FeedbackCommentView.as_view(), 
         name='feedback-comments'),
    path('projects/<int:project_id>/feedbacks/<int:feedback_id>/comments/<int:comment_id>/', 
         views.FeedbackCommentView.as_view(), 
         name='feedback-comment-detail'),
    
    #   
    path('projects/<int:project_id>/feedbacks/upload/init/', 
         views.VideoUploadInitView.as_view(), 
         name='upload-init'),
    path('projects/<int:project_id>/feedbacks/upload/chunk/', 
         views.VideoUploadChunkView.as_view(), 
         name='upload-chunk'),
    path('projects/<int:project_id>/feedbacks/upload/complete/', 
         views.VideoUploadCompleteView.as_view(), 
         name='upload-complete'),
    
    #    
    path('projects/<int:project_id>/feedbacks/<int:feedback_id>/encoding-status/', 
         views.FeedbackEncodingStatusView.as_view(), 
         name='encoding-status'),
    path('projects/<int:project_id>/feedbacks/<int:feedback_id>/stream/', 
         views.FeedbackStreamView.as_view(), 
         name='feedback-stream'),
    
    #      ( )
    path('<int:id>', views.FeedbackDetail.as_view(), name='feedback-detail-legacy'),
]