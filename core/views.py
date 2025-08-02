from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import User, Province, City
from django.contrib import messages
from django.core.files.storage import default_storage
from django.http import JsonResponse

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('core:profile')
        else:
            messages.error(request, 'ایمیل یا رمز عبور اشتباه است')
    return render(request, 'core/login.html')

def user_register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = email
        password = request.POST.get('password')
        confirm = request.POST.get('confirm_password')
        phone = request.POST.get('phone')
        
        if password != confirm:
            messages.error(request, 'رمز عبور و تکرار آن یکسان نیستند')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'این ایمیل قبلاً ثبت شده است')
        else:
            # Extract first name from email (before @ symbol)
            first_name = email.split('@')[0].capitalize()
            
            # Create user with extracted first name
            user = User.objects.create_user(
                email=email, 
                username=username, 
                password=password,
                first_name=first_name,  # Extract from email
                last_name='',           # Empty last name
                phone=phone
            )
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
        
        # Handle province and city
        province_id = request.POST.get('province')
        city_id = request.POST.get('city')
        
        if province_id:
            try:
                user.province = Province.objects.get(id=province_id)
            except Province.DoesNotExist:
                user.province = None
        else:
            user.province = None
            
        if city_id:
            try:
                user.city = City.objects.get(id=city_id)
            except City.DoesNotExist:
                user.city = None
        else:
            user.city = None
        
        if request.FILES.get('profile_image'):
            user.profile_image = request.FILES['profile_image']
        user.save()
        messages.success(request, 'پروفایل با موفقیت ویرایش شد')
        return redirect('core:profile')
    
    provinces = Province.objects.all()
    # Get cities for user's current province if exists
    cities = []
    if user.province:
        cities = City.objects.filter(province=user.province).values('id', 'name')
    
    return render(request, 'core/edit_profile.html', {
        'user': user,
        'provinces': provinces,
        'cities': list(cities)
    })

def get_cities(request):
    """AJAX view to get cities based on selected province"""
    province_id = request.GET.get('province_id')
    if province_id:
        try:
            province = Province.objects.get(id=province_id)
            cities = City.objects.filter(province=province).values('id', 'name')
            return JsonResponse({'cities': list(cities)})
        except Province.DoesNotExist:
            return JsonResponse({'cities': []})
    return JsonResponse({'cities': []})
