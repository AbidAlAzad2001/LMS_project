from django.urls import path
from . import views
from . import instructor_views

urlpatterns = [
    # Student/Public URLs
    path('', views.course_list, name='course_list'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path('my-progress/', views.my_progress, name='my_progress'),
    path('<int:course_id>/enroll-free/', views.enroll_free_course, name='enroll_free_course'),
    path('<slug:slug>/', views.course_detail, name='course_detail'),
    path('<slug:slug>/learn/', views.course_learn, name='course_learn'),
    
    # Reviews
    path('<int:course_id>/review/', views.add_review, name='add_review'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    
    # Lesson completion
    path('lesson/<int:lesson_id>/complete/', views.mark_lesson_complete, name='mark_lesson_complete'),
    path('lesson/<int:lesson_id>/incomplete/', views.mark_lesson_incomplete, name='mark_lesson_incomplete'),
    
    # Certificate
    path('certificate/<str:certificate_id>/download/', views.download_certificate, name='download_certificate'),
    
    # Instructor URLs
    path('instructor/', instructor_views.instructor_dashboard, name='instructor_dashboard'),
    path('instructor/profile/', instructor_views.instructor_profile, name='instructor_profile'),
    path('instructor/courses/', instructor_views.instructor_course_list, name='instructor_course_list'),
    path('instructor/courses/create/', instructor_views.instructor_course_create, name='instructor_course_create'),
    path('instructor/courses/<int:course_id>/edit/', instructor_views.instructor_course_edit, name='instructor_course_edit'),
    path('instructor/courses/<int:course_id>/delete/', instructor_views.instructor_course_delete, name='instructor_course_delete'),
    path('instructor/courses/<int:course_id>/lessons/', instructor_views.instructor_course_lessons, name='instructor_course_lessons'),
    path('instructor/courses/<int:course_id>/lessons/create/', instructor_views.instructor_lesson_create, name='instructor_lesson_create'),
    path('instructor/courses/<int:course_id>/lessons/<int:lesson_id>/edit/', instructor_views.instructor_lesson_edit, name='instructor_lesson_edit'),
    path('instructor/courses/<int:course_id>/lessons/<int:lesson_id>/delete/', instructor_views.instructor_lesson_delete, name='instructor_lesson_delete'),
    path('instructor/courses/<int:course_id>/students/', instructor_views.instructor_enrolled_students, name='instructor_enrolled_students'),
]
