from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes

from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from accounts.models import Profile
from courses.models import Category, Course, Lesson, Enrollment, Review
from payments.models import Payment

from .serializers import (
    RegisterSerializer, LoginSerializer, ProfileSerializer,
    CategorySerializer, CourseListSerializer, CourseDetailSerializer,
    LessonSerializer, EnrollmentSerializer, PaymentSerializer, ReviewSerializer
)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': RegisterSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': RegisterSerializer(user).data
            })
        
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user.profile


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class CourseListView(generics.ListAPIView):
    queryset = Course.objects.filter(is_published=True)
    serializer_class = CourseListSerializer
    permission_classes = [permissions.AllowAny]


class CourseDetailView(generics.RetrieveAPIView):
    queryset = Course.objects.filter(is_published=True)
    serializer_class = CourseDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'


class LessonListView(generics.ListAPIView):
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        course_id = self.kwargs.get('course_id')
        return Lesson.objects.filter(course_id=course_id).order_by('order')


class MyCoursesView(generics.ListAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Enrollment.objects.filter(student=self.request.user.profile)


class EnrollView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id, is_published=True)
        except Course.DoesNotExist:
            return Response(
                {'error': 'Course not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if Enrollment.objects.filter(student=request.user.profile, course=course).exists():
            return Response(
                {'error': 'Already enrolled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not course.is_free:
            return Response(
                {'error': 'This is a paid course. Please use payment.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        enrollment = Enrollment.objects.create(
            student=request.user.profile,
            course=course,
            payment_status='free'
        )
        
        return Response(
            EnrollmentSerializer(enrollment).data,
            status=status.HTTP_201_CREATED
        )


class PaymentStatusView(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user.profile)
    lookup_field = 'transaction_id'


class ReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        course_id = self.kwargs.get('course_id')
        return Review.objects.filter(course_id=course_id).order_by('-created_at')


class ReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        course_id = self.kwargs.get('course_id')
        course = Course.objects.get(id=course_id)
        
        if not Enrollment.objects.filter(student=self.request.user.profile, course=course).exists():
            raise PermissionError("You must enroll in this course to leave a review")
        
        if Review.objects.filter(course=course, student=self.request.user.profile).exists():
            raise PermissionError("You have already reviewed this course")
        
        serializer.save(course=course, student=self.request.user.profile)


class MyReviewsView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Review.objects.filter(student=self.request.user.profile).order_by('-created_at')
