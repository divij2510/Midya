from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('regular', 'Regular User'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='regular')
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def is_owner(self):
        return self.role == 'owner'
    
    def is_admin(self):
        return self.role in ['owner', 'admin']
    
    def __str__(self):
        return self.username

