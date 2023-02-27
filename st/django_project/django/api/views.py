from django.http import JsonResponse
from django.core.handlers.wsgi import WSGIRequest

from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from django.db.backends.utils import CursorWrapper
from helper_dj import get_db_cursor
from .models import *


def index_main(request: WSGIRequest):
    '''Обычное представление Django'''
    return JsonResponse({"status": "ok"})


class ApiView(APIView):
    '''Представления DRF'''
    @get_db_cursor
    def get(self, request: Request, cursor: CursorWrapper):
        ###
        # Сделать SQL запрос
        # cursor.execute('SQL_Запрос')
        # res = cursor.fetchall()
        return Response({"status": "ok"})
