from django import forms
from django.utils.text import slugify
from .models import Course, Category, Lesson, Review


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'category', 'thumbnail', 'short_description', 'description', 'price', 'is_free', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500'}),
            'category': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500'}),
            'short_description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500', 'rows': 3}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500', 'rows': 6}),
            'price': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500'}),
            'is_free': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-indigo-600'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-indigo-600'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
        self.fields['category'].empty_label = 'Select a category'
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.slug = slugify(instance.title)
        if commit:
            instance.save()
        return instance


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'video_url', 'content', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500'}),
            'video_url': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500', 'placeholder': 'https://youtube.com/embed/...'}),
            'content': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500', 'rows': 8}),
            'order': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500'}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500', 'rows': 3}),
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.slug = slugify(instance.name)
        if commit:
            instance.save()
        return instance


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500'}),
            'comment': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500', 'rows': 4, 'placeholder': 'Share your experience (optional)'}),
        }
