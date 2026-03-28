from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings

from courses.models import Course, Enrollment
from .models import Cart, CartItem
from payments.models import Payment
from payments.sslcommerz import sslcommerz_client
import uuid
import json


def get_or_create_cart(user):
    cart, created = Cart.objects.get_or_create(user=user)
    return cart


@login_required
def cart_view(request):
    cart = get_or_create_cart(request.user)
    items = cart.get_items()
    
    context = {
        'cart': cart,
        'items': items,
        'total': cart.get_total(),
    }
    return render(request, 'cart/cart.html', context)


@login_required
def add_to_cart(request, course_id):
    course = get_object_or_404(Course, id=course_id, is_published=True)
    cart = get_or_create_cart(request.user)
    
    if Enrollment.objects.filter(student=request.user.profile, course=course).exists():
        return JsonResponse({'success': False, 'error': 'You are already enrolled in this course'})
    
    if course.is_free:
        return JsonResponse({'success': False, 'error': 'Free courses can be enrolled directly'})
    
    cart_item, created = CartItem.objects.get_or_create(cart=cart, course=course)
    
    if not created:
        return JsonResponse({'success': False, 'error': 'Course already in cart'})
    
    return JsonResponse({
        'success': True, 
        'message': 'Course added to cart',
        'cart_count': cart.get_item_count()
    })


@login_required
def remove_from_cart(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    cart = get_or_create_cart(request.user)
    
    try:
        cart_item = CartItem.objects.get(cart=cart, course=course)
        cart_item.delete()
        return JsonResponse({
            'success': True, 
            'message': 'Course removed from cart',
            'cart_count': cart.get_item_count(),
            'cart_total': cart.get_total()
        })
    except CartItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Course not in cart'})


@login_required
def clear_cart(request):
    cart = get_or_create_cart(request.user)
    cart.items.all().delete()
    messages.success(request, 'Cart cleared')
    return redirect('cart_view')


@login_required
def checkout(request):
    cart = get_or_create_cart(request.user)
    items = cart.get_items()
    
    if not items.exists():
        messages.warning(request, 'Your cart is empty')
        return redirect('cart_view')
    
    paid_items = [item for item in items if not item.course.is_free]
    if not paid_items:
        messages.warning(request, 'No paid courses in cart')
        return redirect('cart_view')
    
    total_amount = sum(item.course.price for item in paid_items)
    transaction_id = f"TRX_{request.user.id}_{uuid.uuid4().hex[:8].upper()}"
    
    payment = Payment.objects.create(
        user=request.user.profile,
        course=paid_items[0].course,
        amount=total_amount,
        transaction_id=transaction_id,
        status='pending',
    )
    
    payment_method = request.POST.get('payment_method', 'card') if request.method == 'POST' else 'card'
    
    if payment_method in ['bkash', 'nogod', 'rocket']:
        demo_url = f"/payments/demo/otp/?tran_id={transaction_id}&amount={total_amount}&method={payment_method}"
        return JsonResponse({
            'success': True,
            'payment_url': demo_url,
        })
    
    result = sslcommerz_client.initiate_payment(
        transaction_id=transaction_id,
        amount=float(total_amount),
        course=paid_items[0].course,
        user=request.user.profile,
    )
    
    if result.get('success'):
        return JsonResponse({
            'success': True,
            'payment_url': result.get('payment_url'),
        })
    else:
        payment.status = 'failed'
        payment.save()
        return JsonResponse({
            'success': False,
            'error': result.get('error', 'Payment initiation failed'),
        })


@login_required
def cart_summary(request):
    cart = get_or_create_cart(request.user)
    items = cart.get_items()
    
    return render(request, 'cart/cart_summary.html', {
        'cart': cart,
        'items': items,
        'total': cart.get_total(),
    })
