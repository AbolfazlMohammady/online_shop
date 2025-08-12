from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import User, Province, City
from django.contrib import messages
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.db.models import F

def home(request):
    """Home page with latest/most viewed products and recent blog posts"""
    from shop.models import Product
    from blog.models import Post

    latest_products = Product.objects.filter(is_active=True).order_by('-created_at')[:5]
    most_viewed_products = Product.objects.filter(is_active=True).order_by('-view_count')[:5]
    recent_posts = Post.objects.filter(status='published').order_by('-published_at')[:3]

    return render(request, 'home.html', {
        'latest_products': latest_products,
        'most_viewed_products': most_viewed_products,
        'recent_posts': recent_posts,
    })

def user_login(request):
    if request.method == 'POST':
        email_or_phone = request.POST.get('email')
        password = request.POST.get('password')
        
        # Validation
        if not email_or_phone:
            messages.error(request, 'لطفاً ایمیل یا شماره موبایل را وارد کنید')
            return render(request, 'core/login.html')
        
        if not password:
            messages.error(request, 'لطفاً رمز عبور را وارد کنید')
            return render(request, 'core/login.html')
        
        # Try to authenticate with email or phone
        user = None
        
        # First try with email
        if '@' in email_or_phone:
            try:
                user_obj = User.objects.get(email=email_or_phone)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        else:
            # Try with phone number
            try:
                user_obj = User.objects.get(phone=email_or_phone)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        
        if user is not None:
            login(request, user)
            messages.success(request, f'خوش آمدید {user.get_full_name() or user.email}!')
            return redirect('core:profile')
        else:
            messages.error(request, 'ایمیل/شماره موبایل یا رمز عبور اشتباه است')
    
    return render(request, 'core/login.html')

def user_register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = email
        password = request.POST.get('password')
        confirm = request.POST.get('confirm_password')
        phone = request.POST.get('phone')
        
        # Phone validation
        if not phone or len(phone) != 11 or not phone.startswith('09'):
            messages.error(request, 'شماره موبایل باید 11 رقم و با 09 شروع شود')
            return render(request, 'core/login.html')
        
        if password != confirm:
            messages.error(request, 'رمز عبور و تکرار آن یکسان نیستند')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'این ایمیل قبلاً ثبت شده است')
        elif User.objects.filter(phone=phone).exists():
            messages.error(request, 'این شماره موبایل قبلاً ثبت شده است')
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
            messages.success(request, f'حساب کاربری شما با موفقیت ایجاد شد! خوش آمدید {user.first_name}!')
            return redirect('core:profile')
    return render(request, 'core/login.html')

def forgot_password(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        verification_code = request.POST.get('verification_code')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Step 1: Phone validation and sending code
        if phone and not verification_code:
            if not phone or len(phone) != 11 or not phone.startswith('09'):
                messages.error(request, 'شماره موبایل باید 11 رقم و با 09 شروع شود')
                return render(request, 'core/login.html')
            
            try:
                user = User.objects.get(phone=phone)
                # Generate verification code (6 digits)
                import random
                code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
                
                # Store code in session for verification
                request.session['verification_code'] = code
                request.session['phone_for_reset'] = phone
                
                # Print code to terminal (simulating SMS)
                print(f"\n{'='*50}")
                print(f"کد تایید برای شماره {phone}: {code}")
                print(f"{'='*50}\n")
                
                messages.success(request, f'کد تایید به شماره {phone} ارسال شد. لطفاً کد را وارد کنید.')
                return redirect('core:login')
                
            except User.DoesNotExist:
                messages.error(request, 'کاربری با این شماره موبایل یافت نشد')
                return render(request, 'core/login.html')
        
        # Step 2: Verify code and change password
        elif verification_code and new_password:
            stored_code = request.session.get('verification_code')
            stored_phone = request.session.get('phone_for_reset')
            
            if not stored_code or not stored_phone:
                messages.error(request, 'لطفاً ابتدا شماره موبایل را وارد کنید')
                return render(request, 'core/login.html')
            
            if verification_code != stored_code:
                messages.error(request, 'کد تایید اشتباه است')
                return render(request, 'core/login.html')
            
            if new_password != confirm_password:
                messages.error(request, 'رمز عبور و تکرار آن یکسان نیستند')
                return render(request, 'core/login.html')
            
            if len(new_password) < 8:
                messages.error(request, 'رمز عبور باید حداقل 8 کاراکتر باشد')
                return render(request, 'core/login.html')
            
            try:
                user = User.objects.get(phone=stored_phone)
                user.set_password(new_password)
                user.save()
                
                # Clear session
                if 'verification_code' in request.session:
                    del request.session['verification_code']
                if 'phone_for_reset' in request.session:
                    del request.session['phone_for_reset']
                
                # Auto login the user after password change
                user = authenticate(request, email=user.email, password=new_password)
                if user is not None:
                    login(request, user)
                    messages.success(request, 'رمز عبور شما با موفقیت تغییر یافت و وارد شدید!')
                    return redirect('core:profile')
                else:
                    messages.success(request, 'رمز عبور شما با موفقیت تغییر یافت. حالا می‌توانید وارد شوید.')
                    return redirect('core:login')
                
            except User.DoesNotExist:
                messages.error(request, 'کاربری با این شماره موبایل یافت نشد')
                return render(request, 'core/login.html')
    
    return render(request, 'core/login.html')

def user_logout(request):
    logout(request)
    return redirect('core:login')

@login_required
def profile(request):
    """Profile view - display user information"""
    user = request.user
    # سفارش‌ها و علاقه‌مندی‌ها برای نمایش در تب‌ها
    from shop.models import Order, Wishlist
    orders = Order.objects.filter(user=user).order_by('-created_at')
    wishlist = None
    try:
        wishlist = Wishlist.objects.get(user=user)
    except Wishlist.DoesNotExist:
        wishlist = None
    return render(request, 'core/profile.html', {
        'user': user,
        'orders': orders,
        'wishlist': wishlist,
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

@login_required
def change_password(request):
    """Change password view"""
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validation
        if not current_password:
            messages.error(request, 'رمز عبور فعلی را وارد کنید')
            return redirect('core:profile')
        
        if not new_password:
            messages.error(request, 'رمز عبور جدید را وارد کنید')
            return redirect('core:profile')
        
        if not confirm_password:
            messages.error(request, 'تکرار رمز عبور جدید را وارد کنید')
            return redirect('core:profile')
        
        if new_password != confirm_password:
            messages.error(request, 'رمزهای عبور جدید مطابقت ندارند')
            return redirect('core:profile')
        
        if len(new_password) < 8:
            messages.error(request, 'رمز عبور جدید باید حداقل 8 کاراکتر باشد')
            return redirect('core:profile')
        
        # Check current password
        user = request.user
        if not user.check_password(current_password):
            messages.error(request, 'رمز عبور فعلی اشتباه است')
            return redirect('core:profile')
        
        # Change password
        user.set_password(new_password)
        user.save()
        
        # Re-login user
        from django.contrib.auth import login
        login(request, user)
        
        messages.success(request, 'رمز عبور با موفقیت تغییر کرد')
        return redirect('core:profile')
    
    return redirect('core:profile')
