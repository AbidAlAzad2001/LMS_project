from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.utils import timezone
from io import BytesIO

try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False

from .models import Course, Lesson, Enrollment, Category, LessonCompletion, Certificate, Review
from .forms import ReviewForm


def course_list(request):
    courses = Course.objects.filter(is_published=True)
    categories = Category.objects.all()
    
    category_slug = request.GET.get('category')
    if category_slug:
        courses = courses.filter(category__slug=category_slug)
    
    paginator = Paginator(courses, 12)
    page = request.GET.get('page')
    courses = paginator.get_page(page)
    
    context = {
        'courses': courses,
        'categories': categories,
        'selected_category': category_slug,
    }
    return render(request, 'courses/course_list.html', context)


def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    lessons = course.lessons.all().order_by('order')
    reviews = course.reviews.all()[:10]
    
    is_enrolled = False
    progress = 0
    user_review = None
    if request.user.is_authenticated:
        enrollment = Enrollment.objects.filter(
            student=request.user.profile,
            course=course
        ).first()
        if enrollment:
            is_enrolled = True
            progress = enrollment.get_progress()
        user_review = Review.objects.filter(course=course, student=request.user.profile).first()
    
    context = {
        'course': course,
        'lessons': lessons,
        'is_enrolled': is_enrolled,
        'progress': progress,
        'reviews': reviews,
        'user_review': user_review,
    }
    return render(request, 'courses/course_detail.html', context)


@login_required
def course_learn(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    
    enrollment = Enrollment.objects.filter(
        student=request.user.profile,
        course=course
    ).first()
    
    if not enrollment:
        messages.error(request, 'You must enroll in this course first.')
        return redirect('course_detail', slug=slug)
    
    lessons = course.lessons.all().order_by('order')
    lesson_id = request.GET.get('lesson')
    
    if lesson_id:
        lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    else:
        lesson = lessons.first()
    
    completed_lessons = LessonCompletion.objects.filter(
        student=request.user.profile,
        lesson__course=course
    ).values_list('lesson_id', flat=True)
    
    progress = enrollment.get_progress()
    course_completed = course.is_completed(request.user.profile)
    
    certificate = None
    if course_completed:
        certificate, created = Certificate.objects.get_or_create(
            student=request.user.profile,
            course=course
        )
    
    context = {
        'course': course,
        'lessons': lessons,
        'current_lesson': lesson,
        'completed_lessons': list(completed_lessons),
        'progress': progress,
        'course_completed': course_completed,
        'certificate': certificate,
    }
    return render(request, 'courses/course_learn.html', context)


@login_required
def my_courses(request):
    enrollments = Enrollment.objects.filter(student=request.user.profile)
    
    enrollment_data = []
    for enrollment in enrollments:
        progress = enrollment.get_progress()
        completed = enrollment.course.is_completed(request.user.profile)
        certificate = Certificate.objects.filter(
            student=request.user.profile,
            course=enrollment.course
        ).first()
        enrollment_data.append({
            'enrollment': enrollment,
            'progress': progress,
            'completed': completed,
            'certificate': certificate,
        })
    
    context = {
        'enrollment_data': enrollment_data,
    }
    return render(request, 'courses/my_courses.html', context)


@login_required
def enroll_free_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, is_published=True, is_free=True)
    
    if Enrollment.objects.filter(student=request.user.profile, course=course).exists():
        messages.info(request, 'You are already enrolled in this course.')
        return redirect('course_detail', slug=course.slug)
    
    Enrollment.objects.create(
        student=request.user.profile,
        course=course,
        payment_status='free'
    )
    
    messages.success(request, f'Successfully enrolled in {course.title}!')
    return redirect('course_learn', slug=course.slug)


@login_required
@require_POST
def mark_lesson_complete(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    
    enrollment = Enrollment.objects.filter(
        student=request.user.profile,
        course=lesson.course
    ).first()
    
    if not enrollment:
        return JsonResponse({'success': False, 'error': 'Not enrolled in this course'})
    
    completion, created = LessonCompletion.objects.get_or_create(
        student=request.user.profile,
        lesson=lesson
    )
    
    if created:
        progress = lesson.course.get_progress_percentage(request.user.profile)
        course_completed = lesson.course.is_completed(request.user.profile)
        
        certificate = None
        if course_completed:
            certificate, cert_created = Certificate.objects.get_or_create(
                student=request.user.profile,
                course=lesson.course
            )
        
        return JsonResponse({
            'success': True,
            'message': 'Lesson marked as complete',
            'progress': progress,
            'course_completed': course_completed,
            'certificate_id': certificate.certificate_id if certificate else None,
        })
    
    return JsonResponse({'success': False, 'error': 'Already completed'})


@login_required
@require_POST
def mark_lesson_incomplete(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    
    try:
        completion = LessonCompletion.objects.get(
            student=request.user.profile,
            lesson=lesson
        )
        completion.delete()
        
        progress = lesson.course.get_progress_percentage(request.user.profile)
        
        Certificate.objects.filter(
            student=request.user.profile,
            course=lesson.course
        ).delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Lesson marked as incomplete',
            'progress': progress,
            'course_completed': False,
        })
    except LessonCompletion.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Not completed'})


@login_required
def download_certificate(request, certificate_id):
    certificate = get_object_or_404(Certificate, certificate_id=certificate_id, student=request.user.profile)
    
    student = request.user
    course = certificate.course
    instructor = course.instructor.user
    
    if WEASYPRINT_AVAILABLE:
        html_string = render_to_string('courses/certificate.html', {
            'certificate': certificate,
            'student': student,
            'course': course,
            'instructor': instructor,
            'issued_date': certificate.issued_at.strftime('%B %d, %Y'),
        })
        
        html = HTML(string=html_string)
        pdf = html.write_pdf()
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="certificate-{certificate.certificate_id}.pdf"'
    else:
        html_string = render_to_string('courses/certificate.html', {
            'certificate': certificate,
            'student': student,
            'course': course,
            'instructor': instructor,
            'issued_date': certificate.issued_at.strftime('%B %d, %Y'),
        })
        
        response = HttpResponse(html_string, content_type='text/html')
        response['Content-Disposition'] = f'attachment; filename="certificate-{certificate.certificate_id}.html"'
    
    return response


@login_required
def my_progress(request):
    enrollments = Enrollment.objects.filter(student=request.user.profile)
    
    total_courses = enrollments.count()
    completed_courses = Certificate.objects.filter(student=request.user.profile).count()
    
    total_lessons = 0
    completed_lessons = LessonCompletion.objects.filter(student=request.user.profile).count()
    
    for enrollment in enrollments:
        total_lessons += enrollment.course.get_lesson_count()
    
    overall_progress = 0
    if total_lessons > 0:
        overall_progress = int((completed_lessons / total_lessons) * 100)
    
    recent_completions = LessonCompletion.objects.filter(
        student=request.user.profile
    ).select_related('lesson', 'lesson__course').order_by('-completed_at')[:10]
    
    context = {
        'total_courses': total_courses,
        'completed_courses': completed_courses,
        'completed_lessons': completed_lessons,
        'overall_progress': overall_progress,
        'remaining_progress': 100 - overall_progress,
        'recent_completions': recent_completions,
    }
    
    return render(request, 'courses/my_progress.html', context)


@login_required
def add_review(request, course_id):
    course = get_object_or_404(Course, id=course_id, is_published=True)
    
    enrollment = Enrollment.objects.filter(
        student=request.user.profile,
        course=course
    ).first()
    
    if not enrollment:
        messages.error(request, 'You must enroll in this course to leave a review.')
        return redirect('course_detail', slug=course.slug)
    
    existing_review = Review.objects.filter(course=course, student=request.user.profile).first()
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=existing_review)
        if form.is_valid():
            review = form.save(commit=False)
            review.course = course
            review.student = request.user.profile
            review.save()
            messages.success(request, 'Your review has been submitted!')
            return redirect('course_detail', slug=course.slug)
    else:
        form = ReviewForm(instance=existing_review)
    
    context = {
        'course': course,
        'form': form,
        'existing_review': existing_review,
    }
    return render(request, 'courses/add_review.html', context)


@login_required
@require_POST
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, student=request.user.profile)
    course_slug = review.course.slug
    review.delete()
    messages.success(request, 'Your review has been deleted.')
    return redirect('course_detail', slug=course_slug)
