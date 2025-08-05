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
    """Profile view - display user information"""
    user = request.user
    return render(request, 'core/profile.html', {
        'user': user
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

def test_messages(request):
    """Test view for messages"""
    messages.success(request, 'پیام موفقیت تست')
    messages.error(request, 'پیام خطا تست')
    messages.warning(request, 'پیام هشدار تست')
    messages.info(request, 'پیام اطلاعات تست')
    return redirect('core:profile')

@login_required
def edit_profile(request):
    """Edit profile view"""
    user = request.user
    if request.method == 'POST':
        try:
            # Get form data
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            phone = request.POST.get('phone', '').strip()
            address = request.POST.get('address', '').strip()
            province_id = request.POST.get('province')
            city_id = request.POST.get('city')
            
            # Validation
            if not first_name:
                messages.error(request, 'نام نمی‌تواند خالی باشد')
                return redirect('core:edit_profile')
            
            if not last_name:
                messages.error(request, 'نام خانوادگی نمی‌تواند خالی باشد')
                return redirect('core:edit_profile')
            
            if not phone:
                messages.error(request, 'شماره موبایل نمی‌تواند خالی باشد')
                return redirect('core:edit_profile')
            
            if not address:
                messages.error(request, 'آدرس نمی‌تواند خالی باشد')
                return redirect('core:edit_profile')
            
            # Update user data
            user.first_name = first_name
            user.last_name = last_name
            user.phone = phone
            user.address = address
            
            # Handle province and city
            if province_id:
                try:
                    user.province = Province.objects.get(id=province_id)
                except Province.DoesNotExist:
                    user.province = None
                    messages.warning(request, 'استان انتخاب شده یافت نشد')
            else:
                user.province = None
                
            if city_id:
                try:
                    user.city = City.objects.get(id=city_id)
                except City.DoesNotExist:
                    user.city = None
                    messages.warning(request, 'شهر انتخاب شده یافت نشد')
            else:
                user.city = None
            
            # Handle profile image
            print(f"DEBUG: request.FILES content: {request.FILES}")
            print(f"DEBUG: request.FILES keys: {list(request.FILES.keys())}")
            if request.FILES.get('profile_image'):
                print(f"DEBUG: Profile image found - {request.FILES['profile_image'].name}")
                print(f"DEBUG: Profile image size: {request.FILES['profile_image'].size}")
                user.profile_image = request.FILES['profile_image']
                print(f"DEBUG: Profile image set to - {user.profile_image}")
            else:
                print("DEBUG: No profile image in request.FILES")
            
            # Save user
            user.save()
            messages.success(request, 'پروفایل با موفقیت ویرایش شد')
            return redirect('core:profile')
            
        except Exception as e:
            messages.error(request, f'خطا در ذخیره پروفایل: {str(e)}')
            return redirect('core:edit_profile')
    
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

@login_required
def test_upload(request):
    """Test upload view"""
    if request.method == 'POST':
        print(f"DEBUG TEST: request.FILES content: {request.FILES}")
        print(f"DEBUG TEST: request.FILES keys: {list(request.FILES.keys())}")
        
        if request.FILES.get('profile_image'):
            file = request.FILES['profile_image']
            print(f"DEBUG TEST: File name: {file.name}")
            print(f"DEBUG TEST: File size: {file.size}")
            print(f"DEBUG TEST: File content type: {file.content_type}")
            
            # Save to user profile
            user = request.user
            user.profile_image = file
            user.save()
            
            messages.success(request, f'فایل {file.name} با موفقیت آپلود شد')
        else:
            messages.error(request, 'هیچ فایلی انتخاب نشده')
    
    return render(request, 'core/test_upload.html')
