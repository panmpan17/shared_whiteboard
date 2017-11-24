# from datetime import datetime
from websocket import create_connection as connect_websocket
from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings

# Create your views here.
def Index(request):
    return render(request, "index.html", {})

def Draw(request, _):
    return render(request, "draw.html", {})
