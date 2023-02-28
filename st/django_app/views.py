from django.core.handlers.wsgi import WSGIRequest

# Create your views here.
from django.http import JsonResponse
from django.shortcuts import render


def index_main(request: WSGIRequest):
    context = {"status": "ok"}
    return JsonResponse(context)
