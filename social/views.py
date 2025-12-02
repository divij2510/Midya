from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Post, Like, Follow, Block, Activity
from .serializers import PostSerializer, LikeSerializer, FollowSerializer, BlockSerializer, ActivitySerializer
from .permissions import IsOwnerOrAdmin

User = get_user_model()


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Post.objects.all()
        
        # Filter out posts from blocked users
        if self.request.user.is_authenticated:
            blocked_ids = self.request.user.blocked_users.values_list('blocked_id', flat=True)
            queryset = queryset.exclude(user_id__in=blocked_ids)
        
        # Filter by user if requested
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        return queryset.select_related('user').prefetch_related('likes')
    
    def perform_create(self, serializer):
        post = serializer.save(user=self.request.user)
        # Create activity
        Activity.objects.create(
            activity_type='post_created',
            actor=self.request.user,
            description=f"{self.request.user.username} made a post"
        )
    
    def destroy(self, request, *args, **kwargs):
        post = self.get_object()
        if not (request.user.is_admin() or post.user == request.user):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        # Create activity
        Activity.objects.create(
            activity_type='post_deleted',
            actor=request.user,
            target_post=post,
            target_user=post.user,
            description=f"Post deleted by '{request.user.username}'"
        )
        
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post', 'delete'])
    def like(self, request, pk=None):
        post = self.get_object()
        
        if request.method == 'POST':
            like, created = Like.objects.get_or_create(user=request.user, post=post)
            if created:
                # Create activity
                Activity.objects.create(
                    activity_type='post_liked',
                    actor=request.user,
                    target_post=post,
                    target_user=post.user,
                    description=f"{request.user.username} liked {post.user.username}'s post"
                )
                return Response({'message': 'Post liked'}, status=status.HTTP_201_CREATED)
            return Response({'message': 'Already liked'}, status=status.HTTP_200_OK)
        
        elif request.method == 'DELETE':
            Like.objects.filter(user=request.user, post=post).delete()
            return Response({'message': 'Post unliked'}, status=status.HTTP_200_OK)


class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Follow.objects.filter(follower=self.request.user)
    
    def create(self, request, *args, **kwargs):
        following_id = request.data.get('following_id')
        if not following_id:
            return Response({'error': 'following_id is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        if int(following_id) == request.user.id:
            return Response({'error': 'Cannot follow yourself'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            following_user = User.objects.get(id=following_id)
            follow, created = Follow.objects.get_or_create(
                follower=request.user,
                following=following_user
            )
            
            if created:
                # Create activity
                Activity.objects.create(
                    activity_type='user_followed',
                    actor=request.user,
                    target_user=following_user,
                    description=f"{request.user.username} followed {following_user.username}"
                )
                return Response(FollowSerializer(follow).data, status=status.HTTP_201_CREATED)
            return Response({'message': 'Already following'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def destroy(self, request, *args, **kwargs):
        follow = self.get_object()
        if follow.follower != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BlockViewSet(viewsets.ModelViewSet):
    serializer_class = BlockSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Block.objects.filter(blocker=self.request.user)
    
    def create(self, request, *args, **kwargs):
        blocked_id = request.data.get('blocked_id')
        if not blocked_id:
            return Response({'error': 'blocked_id is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        if int(blocked_id) == request.user.id:
            return Response({'error': 'Cannot block yourself'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            blocked_user = User.objects.get(id=blocked_id)
            block, created = Block.objects.get_or_create(
                blocker=request.user,
                blocked=blocked_user
            )
            
            if created:
                # Unfollow if following
                Follow.objects.filter(follower=request.user, following=blocked_user).delete()
                # Remove likes from blocked user's posts
                Like.objects.filter(user=request.user, post__user=blocked_user).delete()
                
                return Response(BlockSerializer(block).data, status=status.HTTP_201_CREATED)
            return Response({'message': 'Already blocked'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def destroy(self, request, *args, **kwargs):
        block = self.get_object()
        if block.blocker != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        block.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ActivityViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ActivitySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Get activities from users in the network (followed users + own activities)
        followed_ids = self.request.user.following.values_list('following_id', flat=True)
        user_ids = list(followed_ids) + [self.request.user.id]
        
        queryset = Activity.objects.filter(actor_id__in=user_ids)
        
        # Filter out activities from blocked users
        blocked_ids = self.request.user.blocked_users.values_list('blocked_id', flat=True)
        queryset = queryset.exclude(actor_id__in=blocked_ids)
        
        return queryset.select_related('actor', 'target_user', 'target_post')


class LikeViewSet(viewsets.ModelViewSet):
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Like.objects.filter(user=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        like = self.get_object()
        if not (request.user.is_admin() or like.user == request.user):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        like.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

