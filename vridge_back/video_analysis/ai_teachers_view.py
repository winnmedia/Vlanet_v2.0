"""
AI   
"""
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


# AI  
AI_TEACHERS = [
    {
        "id": 1,
        "name": " ",
        "type": "technical",
        "specialties": [" ", "", " ", " "],
        "description": "      .",
        "avatar": "‍"
    },
    {
        "id": 2,
        "name": " ",
        "type": "creative",
        "specialties": ["", "", "", ""],
        "description": "     .",
        "avatar": "‍"
    },
    {
        "id": 3,
        "name": " ",
        "type": "editing",
        "specialties": [" ", " ", "", " "],
        "description": "     .",
        "avatar": "‍"
    },
    {
        "id": 4,
        "name": " ",
        "type": "marketing",
        "specialties": [" ", " ", "", "CTA"],
        "description": "    .",
        "avatar": "‍"
    }
]


@method_decorator(csrf_exempt, name='dispatch')
class AITeachersListView(View):
    """AI   """
    
    def get(self, request):
        return JsonResponse({
            "status": "success",
            "teachers": AI_TEACHERS,
            "total": len(AI_TEACHERS)
        })
    
    def post(self, request):
        """ AI   """
        import json
        
        try:
            data = json.loads(request.body)
            teacher_id = data.get('teacher_id')
            video_id = data.get('video_id')
            
            #  AI  
            teacher = next((t for t in AI_TEACHERS if t['id'] == teacher_id), None)
            if not teacher:
                return JsonResponse({
                    "status": "error",
                    "message": " AI    ."
                }, status=404)
            
            # TODO:  AI   
            #  Mock  
            return JsonResponse({
                "status": "success",
                "message": f"{teacher['name']}()   .",
                "analysis": {
                    "teacher": teacher,
                    "video_id": video_id,
                    "status": "analyzing",
                    "estimated_time": "2-3"
                }
            })
            
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": f"    : {str(e)}"
            }, status=500)