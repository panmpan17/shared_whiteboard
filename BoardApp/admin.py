from django.contrib import admin
from .models import Report, Board

class BoardAdmin(admin.ModelAdmin):
    pass
 
admin.site.register(Report)
admin.site.register(Board, BoardAdmin)