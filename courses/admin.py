from django.contrib import admin
from .models import Category, Course, Lesson, Enrollment, LessonCompletion, Certificate


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ['title', 'video_url', 'order']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'category', 'price', 'is_free', 'is_published', 'created_at']
    list_filter = ['is_published', 'is_free', 'category', 'created_at']
    search_fields = ['title', 'short_description', 'instructor__user__username']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['instructor']
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'created_at']
    list_filter = ['course', 'created_at']
    search_fields = ['title', 'course__title']
    raw_id_fields = ['course']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'payment_status', 'enrolled_at']
    list_filter = ['payment_status', 'enrolled_at']
    search_fields = ['student__user__username', 'course__title']
    raw_id_fields = ['student', 'course']


@admin.register(LessonCompletion)
class LessonCompletionAdmin(admin.ModelAdmin):
    list_display = ['student', 'lesson', 'completed_at']
    list_filter = ['completed_at', 'lesson__course']
    search_fields = ['student__user__username', 'lesson__title']
    raw_id_fields = ['student', 'lesson']


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['certificate_id', 'student', 'course', 'issued_at']
    list_filter = ['issued_at', 'course']
    search_fields = ['certificate_id', 'student__user__username', 'course__title']
    raw_id_fields = ['student', 'course']
