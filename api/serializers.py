from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from accounts.models import Profile
from courses.models import Category, Course, Lesson, Enrollment, Review
from payments.models import Payment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Profile
        fields = ['id', 'user', 'role', 'phone', 'created_at']


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Password fields did not match.'})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class CategorySerializer(serializers.ModelSerializer):
    course_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'course_count']
    
    def get_course_count(self, obj):
        return obj.courses.filter(is_published=True).count()


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'video_url', 'content', 'order']


class CourseListSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    instructor = serializers.SerializerMethodField()
    lesson_count = serializers.IntegerField(source='get_lesson_count', read_only=True)
    enrolled_count = serializers.IntegerField(source='get_enrolled_count', read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'thumbnail', 'short_description',
            'price', 'is_free', 'category', 'instructor', 'lesson_count',
            'enrolled_count', 'created_at'
        ]
    
    def get_instructor(self, obj):
        return obj.instructor.user.username


class CourseDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    instructor = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    lesson_count = serializers.IntegerField(source='get_lesson_count', read_only=True)
    enrolled_count = serializers.IntegerField(source='get_enrolled_count', read_only=True)
    average_rating = serializers.FloatField(source='get_average_rating', read_only=True)
    review_count = serializers.IntegerField(source='get_review_count', read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'thumbnail', 'short_description',
            'description', 'price', 'is_free', 'category', 'instructor',
            'lessons', 'lesson_count', 'enrolled_count', 'average_rating',
            'review_count', 'created_at'
        ]
    
    def get_instructor(self, obj):
        return {
            'username': obj.instructor.user.username,
            'name': f"{obj.instructor.user.first_name} {obj.instructor.user.last_name}".strip() or obj.instructor.user.username,
        }


class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseListSerializer(read_only=True)
    student = serializers.StringRelatedField(source='student.user', read_only=True)
    
    class Meta:
        model = Enrollment
        fields = ['id', 'course', 'student', 'enrolled_at', 'payment_status']


class PaymentSerializer(serializers.ModelSerializer):
    course = serializers.StringRelatedField(source='course.title', read_only=True)
    
    class Meta:
        model = Payment
        fields = ['id', 'course', 'amount', 'transaction_id', 'status', 'created_at']


class ReviewSerializer(serializers.ModelSerializer):
    student = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = ['id', 'course', 'student', 'rating', 'comment', 'created_at']
    
    def get_student(self, obj):
        return {
            'username': obj.student.user.username,
            'name': f"{obj.student.user.first_name} {obj.student.user.last_name}".strip() or obj.student.user.username,
        }
