from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from accounts.models import Profile
from courses.models import Category, Course, Lesson, Enrollment


class AccountTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_creation(self):
        """Test user is created with profile"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertEqual(self.user.profile.role, 'student')
    
    def test_profile_role_choices(self):
        """Test profile role choices"""
        self.user.profile.role = 'instructor'
        self.user.profile.save()
        self.assertEqual(self.user.profile.role, 'instructor')
        self.assertTrue(self.user.profile.is_instructor)


class CourseTests(TestCase):
    def setUp(self):
        self.instructor_user = User.objects.create_user(
            username='instructor',
            password='testpass123'
        )
        self.instructor = self.instructor_user.profile
        self.instructor.role = 'instructor'
        self.instructor.save()
        
        self.category = Category.objects.create(
            name='Programming',
            slug='programming'
        )
        self.course = Course.objects.create(
            title='Python Basics',
            slug='python-basics',
            category=self.category,
            instructor=self.instructor,
            short_description='Learn Python from scratch',
            description='Full Python course content',
            price=0,
            is_free=True,
            is_published=True
        )
        Lesson.objects.create(
            course=self.course,
            title='Introduction',
            content='Welcome to Python',
            order=1
        )
    
    def test_course_creation(self):
        """Test course is created correctly"""
        self.assertEqual(self.course.title, 'Python Basics')
        self.assertTrue(self.course.is_free)
        self.assertTrue(self.course.is_published)
    
    def test_course_lesson_count(self):
        """Test lesson count method"""
        self.assertEqual(self.course.get_lesson_count(), 1)
    
    def test_course_display_price(self):
        """Test display price method"""
        self.assertEqual(self.course.get_display_price(), 'Free')


class EnrollmentTests(TestCase):
    def setUp(self):
        self.student_user = User.objects.create_user(
            username='student',
            password='testpass123'
        )
        self.student = self.student_user.profile
        
        self.instructor_user = User.objects.create_user(
            username='instructor2',
            password='testpass123'
        )
        self.instructor = self.instructor_user.profile
        self.instructor.role = 'instructor'
        self.instructor.save()
        
        self.category = Category.objects.create(
            name='Web Dev',
            slug='web-dev'
        )
        self.free_course = Course.objects.create(
            title='Free Course',
            slug='free-course',
            category=self.category,
            instructor=self.instructor,
            short_description='Free learning',
            description='Full content',
            is_free=True,
            is_published=True
        )
        self.paid_course = Course.objects.create(
            title='Paid Course',
            slug='paid-course',
            category=self.category,
            instructor=self.instructor,
            short_description='Paid learning',
            description='Full content',
            price=1000,
            is_free=False,
            is_published=True
        )
    
    def test_free_enrollment(self):
        """Test free course enrollment"""
        enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.free_course,
            payment_status='free'
        )
        self.assertEqual(enrollment.payment_status, 'free')
    
    def test_duplicate_enrollment_prevented(self):
        """Test that duplicate enrollments are prevented"""
        Enrollment.objects.create(
            student=self.student,
            course=self.free_course,
            payment_status='free'
        )
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Enrollment.objects.create(
                student=self.student,
                course=self.free_course,
                payment_status='free'
            )


class APITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='apiuser',
            email='api@example.com',
            password='testpass123'
        )
        
        self.instructor_user = User.objects.create_user(
            username='instructor3',
            password='testpass123'
        )
        self.instructor = self.instructor_user.profile
        self.instructor.role = 'instructor'
        self.instructor.save()
        
        self.category = Category.objects.create(
            name='API Test',
            slug='api-test'
        )
        self.course = Course.objects.create(
            title='API Course',
            slug='api-course',
            category=self.category,
            instructor=self.instructor,
            short_description='Test course',
            description='Test content',
            is_free=True,
            is_published=True
        )
    
    def test_course_list_api(self):
        """Test course list API endpoint"""
        response = self.client.get('/api/courses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_course_detail_api(self):
        """Test course detail API endpoint"""
        response = self.client.get(f'/api/courses/{self.course.slug}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'API Course')
    
    def test_register_api(self):
        """Test registration API endpoint"""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123!',
            'password2': 'newpass123!'
        }
        response = self.client.post('/api/auth/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
    
    def test_protected_endpoint_without_auth(self):
        """Test protected endpoint returns 401 without auth"""
        response = self.client.get('/api/profile/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_profile_api_with_auth(self):
        """Test profile endpoint with authentication"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_enroll_api_free_course(self):
        """Test enrollment API for free course"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f'/api/courses/{self.course.id}/enroll/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Enrollment.objects.count(), 1)
    
    def test_enroll_paid_course_fails(self):
        """Test enrollment API fails for paid course"""
        paid_course = Course.objects.create(
            title='Paid',
            slug='paid-api',
            instructor=self.instructor,
            price=100,
            is_free=False,
            is_published=True
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f'/api/courses/{paid_course.id}/enroll/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
