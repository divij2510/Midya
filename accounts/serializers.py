from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'bio', 'profile_picture', 'role']
        extra_kwargs = {
            'email': {'required': True},
            'role': {'required': False},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    posts_count = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()
    can_make_admin = serializers.SerializerMethodField()
    profile_picture_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'bio', 'profile_picture',
                  'followers_count', 'following_count', 'posts_count', 'date_joined',
                  'can_delete', 'can_make_admin', 'profile_picture_url']
        read_only_fields = ['id', 'role', 'date_joined']
    
    def get_profile_picture_url(self, obj):
        if obj.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
        return None
    
    def get_can_delete(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.is_admin() or request.user == obj
        return False
    
    def get_can_make_admin(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.is_owner() and obj.role != 'owner'
        return False
    
    def get_followers_count(self, obj):
        return obj.followers.count()
    
    def get_following_count(self, obj):
        return obj.following.count()
    
    def get_posts_count(self, obj):
        return obj.posts.count()


class UserDetailSerializer(UserSerializer):
    is_following = serializers.SerializerMethodField()
    is_blocked = serializers.SerializerMethodField()
    
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['is_following', 'is_blocked']
    
    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.followers.filter(follower=request.user).exists()
        return False
    
    def get_is_blocked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.blocked_by.filter(blocker=request.user).exists()
        return False

