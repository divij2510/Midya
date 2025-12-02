from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import register, login, profile, UserViewSet, AdminManagementViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'admins', AdminManagementViewSet, basename='admin')

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('profile/', profile, name='profile'),
    path('', include(router.urls)),
]

