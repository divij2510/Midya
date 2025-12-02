from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post, Like, Follow, Block, Activity

User = get_user_model()


class PostSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    user_role = serializers.CharField(source='user.role', read_only=True)
    user_profile_picture_url = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'user', 'user_id', 'user_role', 'user_profile_picture_url', 'content', 'image', 'image_url', 'created_at', 
                  'updated_at', 'likes_count', 'is_liked', 'can_delete']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_user_profile_picture_url(self, obj):
        if obj.user.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.user.profile_picture.url)
        return None
    
    def get_likes_count(self, obj):
        return obj.likes.count()
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
        return None
    
    def get_can_delete(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.is_admin() or obj.user == request.user
        return False


class LikeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    post = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'created_at']
        read_only_fields = ['id', 'created_at']


class FollowSerializer(serializers.ModelSerializer):
    follower = serializers.StringRelatedField(read_only=True)
    follower_id = serializers.IntegerField(source='follower.id', read_only=True)
    following = serializers.StringRelatedField(read_only=True)
    following_id = serializers.IntegerField(source='following.id', read_only=True)
    
    class Meta:
        model = Follow
        fields = ['id', 'follower', 'follower_id', 'following', 'following_id', 'created_at']
        read_only_fields = ['id', 'created_at']


class BlockSerializer(serializers.ModelSerializer):
    blocker = serializers.StringRelatedField(read_only=True)
    blocker_id = serializers.IntegerField(source='blocker.id', read_only=True)
    blocked = serializers.StringRelatedField(read_only=True)
    blocked_id = serializers.IntegerField(source='blocked.id', read_only=True)
    
    class Meta:
        model = Block
        fields = ['id', 'blocker', 'blocker_id', 'blocked', 'blocked_id', 'created_at']
        read_only_fields = ['id', 'created_at']


class ActivitySerializer(serializers.ModelSerializer):
    actor = serializers.StringRelatedField(read_only=True)
    target_user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Activity
        fields = ['id', 'activity_type', 'actor', 'target_user', 'target_post', 
                  'description', 'created_at']
        read_only_fields = ['id', 'created_at']

