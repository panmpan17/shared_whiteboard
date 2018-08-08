from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate
from django.conf import settings

# models
from .models import Report, Board
from django.contrib.auth.models import User

# rest
from BoardApp.serializer import ReportSerializer, BoardSerializer
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import detail_route 
# from rest_framework.parsers import JSONParser

# from websocket import create_connection as connect_ws
from Websocket.encode import new_code

def make_header(args):
    header = []

    for key, value in args.items():
        header.append(f"{key}={value}")

    return "&".join(header)

#django views
def Index(request):
    return render(request, "index.html", {"socket_ip": settings.SOCKET_IP})

def Draw(request, _):
    return render(request, "draw.html", {"socket_ip": settings.SOCKET_IP})

def NewBoard(request):
    username = request.GET.get("username", "")
    password = request.GET.get("password", "")

    user = authenticate(request, username=username, password=password)
    if not user:
        return JsonResponse({
            "success": False,
            "reason": "wrong password"
            })

    return JsonResponse({
            "success": False,
            "code": new_code(),
            })

class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = ()
    # parser_classes = (JSONParser, )

class BoardViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.filter(published=True).values("base64", "create_at")
    serializer_class = BoardSerializer
    
    # def get_queryset(self):
    #   return Board.objects.filter(published=True)