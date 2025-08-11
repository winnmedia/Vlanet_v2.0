# ProjectDate   

@method_decorator(csrf_exempt, name='dispatch')
class ProjectDate(View):
    @user_validator
    def post(self, request, id):
        try:
            user = request.user

            project = models.Project.objects.get_or_none(id=id)
            if project is None:
                return JsonResponse({"message": "    ."}, status=404)

            is_member = models.Members.objects.get_or_none(project=project, user=user, rating="manager")
            if project.user != user and is_member is None:
                return JsonResponse({"message": " ."}, status=403)

            data = json.loads(request.body)
            key = data.get("key")
            start_date = data.get("start_date")
            end_date = data.get("end_date")
            completed = data.get("completed", False)  # completed  

            #     
            process_model_map = {
                'basic_plan': models.BasicPlan,
                'story_board': models.Storyboard,
                'filming': models.Filming,
                'video_edit': models.VideoEdit,
                'post_work': models.PostWork,
                'video_preview': models.VideoPreview,
                'confirmation': models.Confirmation,
                'video_delivery': models.VideoDelivery,
            }
            
            if key not in process_model_map:
                return JsonResponse({"message": f"  : {key}"}, status=400)
            
            #    
            get_process = getattr(project, key)
            
            if get_process is None:
                #     
                ProcessModel = process_model_map[key]
                get_process = ProcessModel.objects.create(
                    start_date=start_date,
                    end_date=end_date
                )
                #  
                setattr(project, key, get_process)
                project.save()
            else:
                #   
                get_process.start_date = start_date
                get_process.end_date = end_date
                
                # completed    (    )
                if hasattr(get_process, 'completed'):
                    get_process.completed = completed
                    
                get_process.save()

            return JsonResponse({"message": "success"}, status=200)

        except Exception as e:
            logger.error(f"Error in project date update: {str(e)}", exc_info=True)
            return JsonResponse({
                "message": "     .",
                "error": str(e)  #   
            }, status=500)