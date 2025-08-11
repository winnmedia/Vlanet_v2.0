import json
import logging
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import transaction
from . import models
from users.utils import user_validator

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class FeedbackMessageReaction(View):
    @user_validator
    def post(self, request, message_id):
        try:
            data = json.loads(request.body)
            reaction_type = data.get('reaction_type')
            
            if reaction_type not in ['like', 'dislike', 'needExplanation']:
                return JsonResponse({"message": "   ."}, status=400)
            
            message = models.FeedBackMessage.objects.get(id=message_id)
            
            with transaction.atomic():
                #     
                reaction, created = models.FeedbackReaction.objects.update_or_create(
                    message=message,
                    user=request.user,
                    defaults={'reaction_type': reaction_type}
                )
            
            #   
            reaction_counts = {}
            for r in message.reactions.all():
                if r.reaction_type not in reaction_counts:
                    reaction_counts[r.reaction_type] = 0
                reaction_counts[r.reaction_type] += 1
            
            return JsonResponse({
                "message": " .",
                "reaction_type": reaction_type,
                "reaction_counts": reaction_counts
            })
            
        except models.FeedBackMessage.DoesNotExist:
            return JsonResponse({"message": "   ."}, status=404)
        except Exception as e:
            logger.error(f"Error in FeedbackMessageReaction: {str(e)}")
            return JsonResponse({"message": "  ."}, status=500)
    
    @user_validator
    def delete(self, request, message_id):
        try:
            message = models.FeedBackMessage.objects.get(id=message_id)
            
            #   
            models.FeedbackReaction.objects.filter(
                message=message,
                user=request.user
            ).delete()
            
            #   
            reaction_counts = {}
            for r in message.reactions.all():
                if r.reaction_type not in reaction_counts:
                    reaction_counts[r.reaction_type] = 0
                reaction_counts[r.reaction_type] += 1
            
            return JsonResponse({
                "message": " .",
                "reaction_counts": reaction_counts
            })
            
        except models.FeedBackMessage.DoesNotExist:
            return JsonResponse({"message": "   ."}, status=404)
        except Exception as e:
            logger.error(f"Error in FeedbackMessageReaction DELETE: {str(e)}")
            return JsonResponse({"message": "  ."}, status=500)
    
    @user_validator
    def get(self, request, message_id):
        try:
            message = models.FeedBackMessage.objects.get(id=message_id)
            
            #  
            reaction_counts = {}
            user_reaction = None
            
            for r in message.reactions.all():
                if r.reaction_type not in reaction_counts:
                    reaction_counts[r.reaction_type] = 0
                reaction_counts[r.reaction_type] += 1
                
                if r.user == request.user:
                    user_reaction = r.reaction_type
            
            return JsonResponse({
                "reaction_counts": reaction_counts,
                "user_reaction": user_reaction
            })
            
        except models.FeedBackMessage.DoesNotExist:
            return JsonResponse({"message": "   ."}, status=404)
        except Exception as e:
            logger.error(f"Error in FeedbackMessageReaction GET: {str(e)}")
            return JsonResponse({"message": "  ."}, status=500)