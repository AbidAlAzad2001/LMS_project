from django.db import models
from django.contrib.auth.models import User
from courses.models import Course


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart for {self.user.username}"
    
    def get_total(self):
        total = 0
        for item in self.items.all():
            if not item.course.is_free:
                total += item.course.price
        return total
    
    def get_item_count(self):
        return self.items.count()
    
    def get_items(self):
        return self.items.select_related('course').all()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['cart', 'course']
    
    def __str__(self):
        return f"{self.course.title} in {self.cart.user.username}'s cart"
    
    @property
    def price(self):
        if self.course.is_free:
            return 0
        return self.course.price
