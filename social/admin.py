from django.contrib import admin
from .models import Post, Like, Follow, Block, Activity


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['user', 'content_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'content']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']
    list_filter = ['created_at']


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['follower', 'following', 'created_at']
    list_filter = ['created_at']


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ['blocker', 'blocked', 'created_at']
    list_filter = ['created_at']


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['activity_type', 'description', 'actor', 'created_at']
    list_filter = ['activity_type', 'created_at']
    search_fields = ['description']

