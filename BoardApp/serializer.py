from rest_framework import serializers
from .models import Report, Board

class ReportSerializer(serializers.ModelSerializer):
	class Meta:
		model = Report
		fields = ("id", "nickname", "email", "content", "create_at")

class BoardSerializer(serializers.ModelSerializer):
	class Meta:
		model = Board
		fields = ("id", "layers", "background", "published", "create_at", "base64")