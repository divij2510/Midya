from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, FollowViewSet, BlockViewSet, ActivityViewSet, LikeViewSet

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')
router.register(r'follows', FollowViewSet, basename='follow')
router.register(r'blocks', BlockViewSet, basename='block')
router.register(r'activities', ActivityViewSet, basename='activity')
router.register(r'likes', LikeViewSet, basename='like')

urlpatterns = [
    path('', include(router.urls)),
]

