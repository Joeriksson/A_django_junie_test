from django.contrib import admin
from .models import DiaryEntry

# Register your models here.
@admin.register(DiaryEntry)
class DiaryEntryAdmin(admin.ModelAdmin):
    list_display = ('date', 'title', 'technologies', 'created_at')
    list_filter = ('date', 'technologies')
    search_fields = ('title', 'content', 'technologies')
    date_hierarchy = 'date'
