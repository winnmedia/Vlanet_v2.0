import logging
from django.shortcuts import render
from . import models
from django.http import JsonResponse
from django.views import View


class OnlineVideo(View):
    def get(self, request):
        try:
            online = list(models.OnlineVideo.objects.all().values("link"))
            return JsonResponse({"result": online}, status=200)
        except Exception as e:
            logging.info(str(e))
            return JsonResponse({"message": "     ."}, status=500)
