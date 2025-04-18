from django.contrib import admin
from .models import DiaryEntry, UserProfile, ReadEntry

# Register your models here.
@admin.register(DiaryEntry)
class DiaryEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'title', 'technologies', 'created_at')
    list_filter = ('user', 'date', 'technologies')
    search_fields = ('title', 'content', 'technologies')
    date_hierarchy = 'date'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_following_count', 'get_followers_count')
    search_fields = ('user__username',)

    def get_following_count(self, obj):
        return obj.following.count()
    get_following_count.short_description = 'Following'

    def get_followers_count(self, obj):
        return obj.get_followers().count()
    get_followers_count.short_description = 'Followers'

@admin.register(ReadEntry)
class ReadEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'entry_title', 'entry_author', 'read_at')
    list_filter = ('user', 'read_at')
    search_fields = ('user__username', 'entry__title')
    date_hierarchy = 'read_at'

    def entry_title(self, obj):
        return obj.entry.title
    entry_title.short_description = 'Entry Title'

    def entry_author(self, obj):
        return obj.entry.user.username
    entry_author.short_description = 'Entry Author'
