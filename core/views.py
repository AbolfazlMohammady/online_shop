from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import User
from django.contrib import messages
from django.core.files.storage import default_storage

def user_login(request):
    if request.method == 'POST':
        login_input = request.POST.get('login')
        password = request.POST.get('password')
        user = authenticate(request, email=login_input, password=password)
        if user is not None:
            login(request, user)
            return redirect('core:profile')
        else:
            messages.error(request, 'ایمیل یا رمز عبور اشتباه است')
    return render(request, 'core/login_register.html')

def user_register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = email
        password = request.POST.get('password')
        confirm = request.POST.get('confirm_password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        profile_image = request.FILES.get('profile_image')
        if password != confirm:
            messages.error(request, 'رمز عبور و تکرار آن یکسان نیستند')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'این ایمیل قبلاً ثبت شده است')
        else:
            user = User.objects.create_user(
                email=email, username=username, password=password,
                first_name=first_name, last_name=last_name, phone=phone, address=address
            )
            if profile_image:
                user.profile_image = profile_image
                user.save()
            login(request, user)
            return redirect('core:profile')
    return render(request, 'core/register.html')

def user_logout(request):
    logout(request)
    return redirect('core:login')

@login_required
def profile(request):
    return render(request, 'core/profile.html', {'user': request.user})

@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.phone = request.POST.get('phone')
        user.address = request.POST.get('address')
        if request.FILES.get('profile_image'):
            user.profile_image = request.FILES['profile_image']
        user.save()
        messages.success(request, 'پروفایل با موفقیت ویرایش شد')
        return redirect('core:profile')
    return render(request, 'core/edit_profile.html', {'user': user})
