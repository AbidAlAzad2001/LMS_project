from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone']
    raw_id_fields = ['user']
