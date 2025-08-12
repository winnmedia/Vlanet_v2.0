from django.urls import path
from . import views
# Conditional import to prevent import errors in Railway
try:
    from . import workflow_views
    has_workflow_views = True
except ImportError:
    has_workflow_views = False
# from . import views_debug
# from . import views_jwt_test
# from . import views_proxy
# from . import views_proposal

app_name = 'video_planning'

urlpatterns = [
    #  
    # path('debug/services/', views_debug.check_services_status, name='check_services_status'),
    # path('debug/test-openai/', views_debug.test_openai_direct, name='test_openai_direct'),
    # path('debug/test-prompt/', views_debug.test_prompt_generation, name='test_prompt_generation'),
    # path('debug/test-jwt/', views_jwt_test.test_jwt_auth, name='test_jwt_auth'),
    # path('debug/test-jwt-protected/', views_jwt_test.test_jwt_protected, name='test_jwt_protected'),
    # path('test-improved-prompts/', views_debug.test_improved_prompts, name='test_improved_prompts'),
    
    #   
    path('', views.get_planning_list, name='planning_list_default'),
    path('create/', views.save_planning, name='create_planning'),
    
    #   API
    path('generate/structure/', views.generate_structure, name='generate_structure'),
    path('generate/story/', views.generate_story, name='generate_story'),
    path('generate/scenes/', views.generate_scenes, name='generate_scenes'),
    path('generate/shots/', views.generate_shots, name='generate_shots'),
    path('generate/storyboards/', views.generate_storyboards, name='generate_storyboards'),
    path('generate/all-storyboards/', views.generate_all_storyboards, name='generate_all_storyboards'),
    
    #   API
    path('regenerate/storyboard-image/', views.regenerate_storyboard_image, name='regenerate_storyboard_image'),
    path('download/storyboard-image/', views.download_storyboard_image, name='download_storyboard_image'),
    path('generate/storyboard-images-async/', views.generate_storyboard_images_async, name='generate_storyboard_images_async'),
    path('check-image-generation-status/<str:task_id>/', views.check_image_generation_status, name='check_image_generation_status'),
    # path('proxy/image/', views_proxy.proxy_image, name='proxy_image'),
    # path('convert/base64/', views_proxy.convert_to_base64, name='convert_to_base64'),
    
    #  / API
    path('save/', views.save_planning, name='save_planning'),
    path('list/', views.get_planning_list, name='get_planning_list'),
    path('detail/<int:planning_id>/', views.get_planning_detail, name='get_planning_detail'),
    path('update/<int:planning_id>/', views.update_planning, name='update_planning'),
    path('delete/<int:planning_id>/', views.delete_planning, name='delete_planning'),
    
    #    API
    path('recent/', views.get_recent_plannings, name='get_recent_plannings'),
    
    # 통합 워크플로우 API (조건부 추가)
    
    #  API (  )
    path('library/', views.planning_library_view, name='planning_library'),
    path('library/<int:planning_id>/', views.get_planning_detail, name='get_planning_detail_library'),
    
    #  API
    path('export/pdf/', views.export_to_pdf, name='export_to_pdf'),
    path('export/pdf-advanced/', views.export_to_advanced_pdf, name='export_to_advanced_pdf'),
    path('export/pdf-enhanced/', views.export_to_enhanced_pdf, name='export_to_enhanced_pdf'),
    path('export/google-slides/', views.export_to_google_slides, name='export_to_google_slides'),
    path('export/formats/', views.get_export_formats, name='get_export_formats'),
    
    #   API ( AI )
    # path('proposals/export/', views_proposal.export_proposal, name='export_proposal'),
    # path('proposals/preview/', views_proposal.preview_structure, name='preview_structure'),
    # path('proposals/create-slides/', views_proposal.create_slides_from_structure, name='create_slides_from_structure'),
    # path('proposals/templates/', views_proposal.get_available_templates, name='get_available_templates'),
    # path('proposals/status/', views_proposal.get_service_status, name='get_service_status'),
    
    # AI   API ( 1000%  )
    path('ai/generate-prompt/', views.generate_ai_prompt, name='generate_ai_prompt'),
    path('ai/prompt-analytics/<int:planning_id>/', views.get_prompt_analytics, name='get_prompt_analytics'),
    path('ai/prompt-history/<int:planning_id>/', views.get_prompt_history, name='get_prompt_history'),
    
    #   API
    path('pro/settings/<int:planning_id>/', views.update_pro_settings, name='update_pro_settings'),
    path('pro/templates/', views.get_pro_templates, name='get_pro_templates'),
    path('pro/templates/<int:planning_id>/<int:template_id>/apply/', views.apply_pro_template, name='apply_pro_template'),
    
    # AI  30   API
    path('ai/quick-suggestions/', views.ai_quick_suggestions, name='ai_quick_suggestions'),
    path('ai/generate-full-planning/', views.ai_generate_full_planning, name='ai_generate_full_planning'),
    path('ai/generate-veo3-prompt/', views.generate_veo3_prompt, name='generate_veo3_prompt'),
    
    #   API
    path('complete/', views.complete_project, name='complete_project'),
]

# 조건부로 workflow URLs 추가
if has_workflow_views:
    urlpatterns.extend([
        path('workflow/complete/', workflow_views.complete_workflow, name='complete_workflow'),
        path('workflow/status/<int:planning_id>/', workflow_views.get_workflow_status, name='workflow_status'),
    ])