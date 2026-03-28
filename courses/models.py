from django.db import models
from django.contrib.auth.models import User
from accounts.models import Profile
import uuid


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Course(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='courses')
    instructor = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='courses')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    thumbnail = models.ImageField(upload_to='courses/thumbnails/', blank=True, null=True)
    short_description = models.TextField(max_length=300)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_free = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_lesson_count(self):
        return self.lessons.count()
    
    def get_enrolled_count(self):
        return self.enrollments.count()
    
    def get_display_price(self):
        if self.is_free:
            return 'Free'
        return f'৳{self.price}'
    
    def get_first_lesson(self):
        return self.lessons.order_by('order').first()
    
    def get_completed_count(self, student):
        return self.lessons.filter(completions__student=student).count()
    
    def get_progress_percentage(self, student):
        total = self.get_lesson_count()
        if total == 0:
            return 0
        completed = self.get_completed_count(student)
        return int((completed / total) * 100)
    
    def is_completed(self, student):
        total = self.get_lesson_count()
        if total == 0:
            return False
        completed = self.get_completed_count(student)
        return completed == total
    
    def get_average_rating(self):
        reviews = self.reviews.all()
        if not reviews:
            return 0
        return round(sum(r.rating for r in reviews) / len(reviews), 1)
    
    def get_review_count(self):
        return self.reviews.count()


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    video_url = models.CharField(max_length=500, blank=True)
    content = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Enrollment(models.Model):
    student = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20, default='free')
    
    class Meta:
        unique_together = ['student', 'course']
        ordering = ['-enrolled_at']
    
    def __str__(self):
        return f"{self.student.user.username} - {self.course.title}"
    
    def get_progress(self):
        total = self.course.get_lesson_count()
        if total == 0:
            return 0
        completed = LessonCompletion.objects.filter(student=self.student, lesson__course=self.course).count()
        return int((completed / total) * 100)


class LessonCompletion(models.Model):
    student = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='lesson_completions')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='completions')
    completed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'lesson']
        ordering = ['completed_at']
    
    def __str__(self):
        return f"{self.student.user.username} - {self.lesson.title}"


class Certificate(models.Model):
    certificate_id = models.CharField(max_length=50, unique=True, editable=False)
    student = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='certificates')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='certificates')
    issued_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'course']
        ordering = ['-issued_at']
    
    def save(self, *args, **kwargs):
        if not self.certificate_id:
            self.certificate_id = f"CERT-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.student.user.username} - {self.course.title}"


class Review(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    student = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['course', 'student']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.user.username} - {self.course.title} ({self.rating}★)"
