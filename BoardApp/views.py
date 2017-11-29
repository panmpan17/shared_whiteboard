# from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.conf import settings

# models
from .models import Report, Board

# rest
from BoardApp.serializer import ReportSerializer, BoardSerializer
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import detail_route
# from rest_framework.parsers import JSONParser

# Create your views here.
def Index(request):
    return render(request, "index.html", {"socket_ip": settings.SOCKET_IP})

def Draw(request, _):
    return render(request, "draw.html", {"socket_ip": settings.SOCKET_IP})

class ReportViewSet(viewsets.ModelViewSet):
	queryset = Report.objects.all()
	serializer_class = ReportSerializer
	permission_classes = ()
	# parser_classes = (JSONParser, )

class BoardViewSet(viewsets.ModelViewSet):
	queryset = Board.objects.filter(published=True).values('base64', 'create_at')
	serializer_class = BoardSerializer
	
	# def get_queryset(self):
	# 	return Board.objects.filter(published=True)