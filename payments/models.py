from django.db import models
from django.contrib.auth.models import User
from courses.models import Course, Profile


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='payments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, unique=True)
    val_id = models.CharField(max_length=100, blank=True)
    card_type = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    raw_response = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.user.username} - {self.course.title} - {self.transaction_id}"
