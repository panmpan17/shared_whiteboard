from django.db import models

# Create your models here.
class Report(models.Model):
	nickname = models.CharField(max_length=20)
	email = models.CharField(max_length=35)
	content = models.TextField(blank=False)
	create_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.nickname

	class Meta:
		db_table = "report"

class Board(models.Model):
	layers = models.TextField(blank=True)
	background = models.TextField(blank=True)
	published = models.BooleanField(default=False)
	create_at = models.DateTimeField(auto_now_add=True)
	base64 = models.TextField(blank=True)

	class Meta:
		db_table = "board"