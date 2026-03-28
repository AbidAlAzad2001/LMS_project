from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import uuid
import json

from courses.models import Course, Enrollment
from .models import Payment
from .sslcommerz import sslcommerz_client


@login_required
def checkout(request, course_id):
    course = get_object_or_404(Course, id=course_id, is_published=True)
    
    if Enrollment.objects.filter(student=request.user.profile, course=course).exists():
        messages.info(request, 'You are already enrolled in this course.')
        return redirect('course_learn', slug=course.slug)
    
    if course.is_free:
        return redirect('enroll_free_course', course_id=course.id)
    
    context = {
        'course': course,
    }
    return render(request, 'payments/checkout.html', context)


@login_required
def initiate_payment(request, course_id):
    course = get_object_or_404(Course, id=course_id, is_published=True)
    
    if Enrollment.objects.filter(student=request.user.profile, course=course).exists():
        return JsonResponse({'success': False, 'error': 'Already enrolled'})
    
    if course.is_free:
        return JsonResponse({'success': False, 'error': 'This course is free'})
    
    payment_method = request.POST.get('payment_method', 'card')
    
    transaction_id = f"TRX_{request.user.id}_{course.id}_{uuid.uuid4().hex[:8].upper()}"
    
    payment = Payment.objects.create(
        user=request.user.profile,
        course=course,
        amount=course.price,
        transaction_id=transaction_id,
        status='pending',
    )
    
    if payment_method in ['bkash', 'nogod', 'rocket']:
        demo_url = f"/payments/demo/otp/?tran_id={transaction_id}&amount={course.price}&method={payment_method}"
        return JsonResponse({
            'success': True,
            'payment_url': demo_url,
        })
    
    result = sslcommerz_client.initiate_payment(
        transaction_id=transaction_id,
        amount=float(course.price),
        course=course,
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
def payment_success(request):
    val_id = request.GET.get('val_id', '')
    tran_id = request.GET.get('tran_id', '')
    
    try:
        payment = Payment.objects.get(transaction_id=tran_id)
        
        if payment.status == 'success':
            messages.success(request, 'Payment already processed!')
            return redirect('course_learn', slug=payment.course.slug)
        
        verify_result = sslcommerz_client.verify_payment(request.GET.dict())
        
        if verify_result.get('valid'):
            payment.status = 'success'
            payment.val_id = val_id
            payment.raw_response = json.dumps(request.GET.dict())
            payment.save()
            
            enrollment, created = Enrollment.objects.get_or_create(
                student=payment.user,
                course=payment.course,
                defaults={'payment_status': 'paid'}
            )
            if created:
                enrollment.payment_status = 'paid'
                enrollment.save()
            
            messages.success(request, f'Payment successful! You are now enrolled in {payment.course.title}')
            return redirect('course_learn', slug=payment.course.slug)
        else:
            payment.status = 'failed'
            payment.raw_response = json.dumps(request.GET.dict())
            payment.save()
            messages.error(request, 'Payment verification failed.')
            
    except Payment.DoesNotExist:
        messages.error(request, 'Payment not found.')
    except Exception as e:
        messages.error(request, f'Error processing payment: {str(e)}')
    
    return redirect('dashboard')


def payment_fail(request):
    tran_id = request.GET.get('tran_id', '')
    
    try:
        payment = Payment.objects.get(transaction_id=tran_id)
        payment.status = 'failed'
        payment.raw_response = json.dumps(request.GET.dict())
        payment.save()
        messages.error(request, 'Payment failed. Please try again.')
    except Payment.DoesNotExist:
        messages.error(request, 'Payment not found.')
    
    return render(request, 'payments/fail.html')


def payment_cancel(request):
    tran_id = request.GET.get('tran_id', '')
    
    try:
        payment = Payment.objects.get(transaction_id=tran_id)
        payment.status = 'cancelled'
        payment.raw_response = json.dumps(request.GET.dict())
        payment.save()
        messages.warning(request, 'Payment was cancelled.')
    except Payment.DoesNotExist:
        messages.warning(request, 'Payment not found.')
    
    return render(request, 'payments/cancel.html')


@csrf_exempt
def payment_ipn(request):
    """Instant Payment Notification handler from SSLCommerz.
    
    This endpoint receives payment status updates from SSLCommerz.
    Important for production to ensure payment completion.
    """
    if request.method == 'POST':
        post_data = request.POST.dict()
        tran_id = post_data.get('tran_id', '')
        status = post_data.get('status', '')
        
        try:
            payment = Payment.objects.get(transaction_id=tran_id)
            
            if status == 'VALID':
                if payment.status != 'success':
                    payment.status = 'success'
                    payment.raw_response = json.dumps(post_data)
                    payment.save()
                    
                    enrollment, created = Enrollment.objects.get_or_create(
                        student=payment.user,
                        course=payment.course,
                        defaults={'payment_status': 'paid'}
                    )
                    if created:
                        enrollment.payment_status = 'paid'
                        enrollment.save()
                        
        except Payment.DoesNotExist:
            pass
    
    return JsonResponse({'status': 'OK'})


def demo_payment_otp(request):
    tran_id = request.GET.get('tran_id', '')
    amount = request.GET.get('amount', '0')
    payment_method = request.GET.get('method', 'card')
    
    context = {
        'tran_id': tran_id,
        'amount': amount,
        'payment_method': payment_method,
    }
    return render(request, 'payments/demo_otp.html', context)


@login_required
def demo_payment_verify(request):
    if request.method == 'POST':
        tran_id = request.POST.get('tran_id', '')
        amount = request.POST.get('amount', '0')
        payment_method = request.POST.get('payment_method', 'card')
        otp = request.POST.get('otp', '')
        
        if otp != '123456':
            messages.error(request, 'Invalid OTP. Please use 123456 for demo.')
            return redirect('demo_payment_otp')
        
        try:
            payment = Payment.objects.get(transaction_id=tran_id)
            
            if payment.status == 'success':
                messages.success(request, 'Payment already processed!')
                return redirect('course_learn', slug=payment.course.slug)
            
            payment.status = 'success'
            payment.val_id = f'DEMO_{uuid.uuid4().hex[:12].upper()}'
            payment.raw_response = json.dumps({
                'demo': True,
                'payment_method': payment_method,
                'otp_verified': True,
            })
            payment.save()
            
            enrollment, created = Enrollment.objects.get_or_create(
                student=payment.user,
                course=payment.course,
                defaults={'payment_status': 'paid'}
            )
            if created:
                enrollment.payment_status = 'paid'
                enrollment.save()
            
            messages.success(request, f'Payment successful! You are now enrolled in {payment.course.title}')
            
            return render(request, 'payments/demo_success.html', {
                'tran_id': tran_id,
                'amount': amount,
                'payment_method': payment_method,
                'course_slug': payment.course.slug,
            })
            
        except Payment.DoesNotExist:
            messages.error(request, 'Payment not found.')
            return redirect('dashboard')
    
    return redirect('dashboard')
