from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Q, Count, Exists, OuterRef
from .models import Post, Like, Follow, Block, Activity
from .serializers import PostSerializer, ActivitySerializer
from accounts.serializers import UserSerializer, UserDetailSerializer

User = get_user_model()


def home(request):
    if request.user.is_authenticated:
        return redirect('feed')
    return redirect('login_page')


def login_page(request):
    if request.user.is_authenticated:
        return redirect('feed')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('feed')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'social/login.html')


def register_page(request):
    if request.user.is_authenticated:
        return redirect('feed')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        bio = request.POST.get('bio', '')
        profile_picture = request.FILES.get('profile_picture')
        
        if password != password2:
            messages.error(request, 'Passwords do not match')
        else:
            try:
                user = User.objects.create_user(username=username, email=email, password=password, bio=bio)
                if profile_picture:
                    user.profile_picture = profile_picture
                    user.save()
                login(request, user)
                return redirect('feed')
            except Exception as e:
                messages.error(request, str(e))
    
    return render(request, 'social/register.html')


def logout_page(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('login_page')


@login_required
def feed(request):
    # Get activities from users in network
    followed_ids = request.user.following.values_list('following_id', flat=True)
    user_ids = list(followed_ids) + [request.user.id]
    
    # Filter out blocked users
    blocked_ids = request.user.blocked_users.values_list('blocked_id', flat=True)
    user_ids = [uid for uid in user_ids if uid not in blocked_ids]
    
    activities = Activity.objects.filter(actor_id__in=user_ids).exclude(actor_id__in=blocked_ids).order_by('-created_at')[:50]
    activity_serializer = ActivitySerializer(activities, many=True, context={'request': request})
    
    # Get posts (excluding blocked users)
    posts = Post.objects.exclude(user_id__in=blocked_ids).select_related('user').prefetch_related('likes').order_by('-created_at')[:50]
    post_serializer = PostSerializer(posts, many=True, context={'request': request})
    
    context = {
        'activities': activity_serializer.data,
        'posts': post_serializer.data,
        'user': request.user,
    }
    return render(request, 'social/feed.html', context)


@login_required
def create_post(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        image = request.FILES.get('image')
        
        try:
            post = Post.objects.create(user=request.user, content=content, image=image)
            # Create activity
            Activity.objects.create(
                activity_type='post_created',
                actor=request.user,
                description=f"{request.user.username} made a post"
            )
            messages.success(request, 'Post created successfully')
            return redirect('feed')
        except Exception as e:
            messages.error(request, str(e))
    
    return render(request, 'social/create_post.html')


@login_required
def users_list(request):
    # Show all users (blocked users are still visible, just their posts are hidden)
    users = User.objects.annotate(
        followers_count=Count('followers'),
        following_count=Count('following'),
        posts_count=Count('posts')
    )
    
    user_serializer = UserDetailSerializer(users, many=True, context={'request': request})
    
    context = {
        'users': user_serializer.data,
        'user': request.user,
    }
    return render(request, 'social/users.html', context)


@login_required
def user_profile(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    
    # Get user posts - filter out if user is blocked
    posts = Post.objects.filter(user=profile_user)
    
    # Filter out posts if the profile user is blocked by current user
    blocked_ids = request.user.blocked_users.values_list('blocked_id', flat=True)
    if profile_user.id in blocked_ids:
        posts = posts.none()  # Return empty queryset - user can see profile but not posts
    
    posts = posts.select_related('user').prefetch_related('likes').order_by('-created_at')
    post_serializer = PostSerializer(posts, many=True, context={'request': request})
    
    # Serialize user
    user_serializer = UserDetailSerializer(profile_user, context={'request': request})
    
    context = {
        'profile_user': user_serializer.data,
        'posts': post_serializer.data,
        'user': request.user,
    }
    return render(request, 'social/profile.html', context)

