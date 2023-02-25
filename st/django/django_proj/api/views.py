from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.core.handlers.wsgi import WSGIRequest


def index_main(request: WSGIRequest):
    context = {"status": "ok"}
    return JsonResponse(context)
