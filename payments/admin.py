from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'user', 'course', 'amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['transaction_id', 'user__user__username', 'course__title']
    raw_id_fields = ['user', 'course']
    readonly_fields = ['transaction_id', 'created_at', 'updated_at', 'raw_response']
