from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from courses.models import Course, Category, Enrollment, LessonCompletion, Certificate


def home(request):
    featured_courses = Course.objects.filter(is_published=True)[:6]
    categories = Category.objects.all()
    
    context = {
        'featured_courses': featured_courses,
        'categories': categories,
    }
    return render(request, 'core/home.html', context)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        profile = self.request.user.profile
        enrollments = profile.enrollments.all()[:5]
        
        courses_count = enrollments.count()
        completed_count = Certificate.objects.filter(student=profile).count()
        lessons_done = LessonCompletion.objects.filter(student=profile).count()
        
        total_lessons = 0
        for enrollment in profile.enrollments.all():
            total_lessons += enrollment.course.get_lesson_count()
        
        overall_progress = 0
        if total_lessons > 0:
            overall_progress = int((lessons_done / total_lessons) * 100)
        
        context['enrollments'] = enrollments
        context['courses_count'] = courses_count
        context['completed_count'] = completed_count
        context['lessons_done'] = lessons_done
        context['overall_progress'] = overall_progress
        
        return context
