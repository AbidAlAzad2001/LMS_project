from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.db.models import Count, Q

from accounts.forms import UserUpdateForm, ProfileUpdateForm
from .models import Course, Category, Lesson, Enrollment
from .forms import CourseForm, LessonForm


class InstructorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.profile.is_instructor
    
    def handle_no_permission(self):
        messages.error(self.request, 'You must be an instructor to access this page.')
        return redirect('dashboard')


@login_required
def instructor_dashboard(request):
    if not request.user.profile.is_instructor:
        messages.error(request, 'You must be an instructor to access this page.')
        return redirect('dashboard')
    
    courses = Course.objects.filter(instructor=request.user.profile)
    total_students = Enrollment.objects.filter(course__instructor=request.user.profile).values('student').distinct().count()
    total_enrollments = Enrollment.objects.filter(course__instructor=request.user.profile).count()
    total_courses = courses.count()
    
    context = {
        'courses': courses,
        'total_students': total_students,
        'total_enrollments': total_enrollments,
        'total_courses': total_courses,
    }
    return render(request, 'courses/instructor_dashboard.html', context)


@login_required
def instructor_profile(request):
    if not request.user.profile.is_instructor:
        messages.error(request, 'You must be an instructor to access this page.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('instructor_profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    
    return render(request, 'courses/instructor_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


@login_required
def instructor_course_list(request):
    if not request.user.profile.is_instructor:
        messages.error(request, 'You must be an instructor to access this page.')
        return redirect('dashboard')
    
    courses = Course.objects.filter(instructor=request.user.profile)
    return render(request, 'courses/instructor_course_list.html', {'courses': courses})


@login_required
def instructor_course_create(request):
    if not request.user.profile.is_instructor:
        messages.error(request, 'You must be an instructor to access this page.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user.profile
            course.save()
            messages.success(request, f'Course "{course.title}" created successfully!')
            return redirect('instructor_course_list')
    else:
        form = CourseForm()
    
    return render(request, 'courses/instructor_course_form.html', {'form': form, 'action': 'Create'})


@login_required
def instructor_course_edit(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user.profile)
    
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, f'Course "{course.title}" updated successfully!')
            return redirect('instructor_course_list')
    else:
        form = CourseForm(instance=course)
    
    return render(request, 'courses/instructor_course_form.html', {'form': form, 'course': course, 'action': 'Edit'})


@login_required
def instructor_course_delete(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user.profile)
    
    if request.method == 'POST':
        course.delete()
        messages.success(request, f'Course "{course.title}" deleted successfully!')
        return redirect('instructor_course_list')
    
    return render(request, 'courses/instructor_course_confirm_delete.html', {'course': course})


@login_required
def instructor_course_lessons(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user.profile)
    lessons = course.lessons.all().order_by('order')
    return render(request, 'courses/instructor_course_lessons.html', {'course': course, 'lessons': lessons})


@login_required
def instructor_lesson_create(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user.profile)
    
    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course
            lesson.save()
            messages.success(request, f'Lesson "{lesson.title}" added successfully!')
            return redirect('instructor_course_lessons', course_id=course.id)
    else:
        form = LessonForm()
    
    return render(request, 'courses/instructor_lesson_form.html', {'form': form, 'course': course, 'action': 'Add'})


@login_required
def instructor_lesson_edit(request, course_id, lesson_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user.profile)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    
    if request.method == 'POST':
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, f'Lesson "{lesson.title}" updated successfully!')
            return redirect('instructor_course_lessons', course_id=course.id)
    else:
        form = LessonForm(instance=lesson)
    
    return render(request, 'courses/instructor_lesson_form.html', {'form': form, 'course': course, 'lesson': lesson, 'action': 'Edit'})


@login_required
def instructor_lesson_delete(request, course_id, lesson_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user.profile)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    
    if request.method == 'POST':
        lesson.delete()
        messages.success(request, f'Lesson deleted successfully!')
        return redirect('instructor_course_lessons', course_id=course.id)
    
    return render(request, 'courses/instructor_lesson_confirm_delete.html', {'course': course, 'lesson': lesson})


@login_required
def instructor_enrolled_students(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user.profile)
    enrollments = Enrollment.objects.filter(course=course).select_related('student__user')
    return render(request, 'courses/instructor_enrolled_students.html', {'course': course, 'enrollments': enrollments})
