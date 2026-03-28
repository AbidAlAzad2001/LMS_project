from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class Profile(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('instructor', 'Instructor'),
        ('admin', 'Admin'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    phone = models.CharField(max_length=20, blank=True)
    email_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=64, blank=True)
    token_created_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"
    
    @property
    def is_instructor(self):
        return self.role in ['instructor', 'admin']
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    def generate_verification_token(self):
        self.verification_token = uuid.uuid4().hex
        self.token_created_at = timezone.now()
        self.save()
        return self.verification_token
    
    def is_token_valid(self):
        if not self.verification_token or not self.token_created_at:
            return False
        expiry = self.token_created_at + timezone.timedelta(days=1)
        return timezone.now() < expiry
