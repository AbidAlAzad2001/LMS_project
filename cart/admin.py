from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['course', 'added_at']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_item_count', 'created_at', 'updated_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CartItemInline]
    
    def get_item_count(self, obj):
        return obj.get_item_count()
    get_item_count.short_description = 'Items'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['course', 'cart', 'added_at']
    list_filter = ['added_at']
    search_fields = ['course__title', 'cart__user__username']
    readonly_fields = ['added_at']
