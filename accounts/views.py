from rest_framework import status, generics, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model, authenticate
from .serializers import UserRegistrationSerializer, UserSerializer, UserDetailSerializer
from social.permissions import IsOwnerOrAdmin, IsOwner

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    if username and password:
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            })
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    serializer = UserDetailSerializer(request.user, context={'request': request})
    return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserDetailSerializer
        return UserSerializer
    
    def get_queryset(self):
        # Show all users (blocked users are still visible, just their posts are hidden)
        return User.objects.all()
    
    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        if not (request.user.is_admin() or request.user == user):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        # Create activity
        from social.models import Activity
        Activity.objects.create(
            activity_type='user_deleted',
            actor=request.user,
            target_user=user,
            description=f"User deleted by '{request.user.username}'"
        )
        
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminManagementViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(role__in=['admin', 'owner'])
    serializer_class = UserSerializer
    permission_classes = [IsOwner]
    
    def create(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        try:
            user = User.objects.get(id=user_id)
            if user.role == 'owner':
                return Response({'error': 'Cannot modify owner role'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            user.role = 'admin'
            user.save()
            return Response(UserSerializer(user).data)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        if user.role == 'owner':
            return Response({'error': 'Cannot delete owner'}, status=status.HTTP_400_BAD_REQUEST)
        user.role = 'regular'
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

