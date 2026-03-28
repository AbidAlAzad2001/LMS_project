from django.urls import path
from . import views

urlpatterns = [
    path('auth/register/', views.RegisterView.as_view(), name='api_register'),
    path('auth/login/', views.LoginView.as_view(), name='api_login'),
    path('profile/', views.ProfileView.as_view(), name='api_profile'),
    path('categories/', views.CategoryListView.as_view(), name='api_categories'),
    path('courses/', views.CourseListView.as_view(), name='api_courses'),
    path('courses/<slug:slug>/', views.CourseDetailView.as_view(), name='api_course_detail'),
    path('courses/<int:course_id>/lessons/', views.LessonListView.as_view(), name='api_lessons'),
    path('courses/<int:course_id>/enroll/', views.EnrollView.as_view(), name='api_enroll'),
    path('courses/<int:course_id>/reviews/', views.ReviewListView.as_view(), name='api_reviews'),
    path('courses/<int:course_id>/reviews/create/', views.ReviewCreateView.as_view(), name='api_review_create'),
    path('my-courses/', views.MyCoursesView.as_view(), name='api_my_courses'),
    path('my-reviews/', views.MyReviewsView.as_view(), name='api_my_reviews'),
    path('payments/<str:transaction_id>/status/', views.PaymentStatusView.as_view(), name='api_payment_status'),
]
