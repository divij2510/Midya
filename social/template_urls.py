from django.urls import path
from .template_views import home, login_page, register_page, feed, create_post, users_list, user_profile, logout_page

urlpatterns = [
    path('', home, name='home'),
    path('login/', login_page, name='login_page'),
    path('register/', register_page, name='register_page'),
    path('logout/', logout_page, name='logout_page'),
    path('feed/', feed, name='feed'),
    path('create-post/', create_post, name='create_post'),
    path('users/', users_list, name='users_list'),
    path('users/<int:user_id>/', user_profile, name='user_profile'),
]

