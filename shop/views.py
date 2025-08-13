from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from .models import Product, Cart, CartItem, Wishlist, Settings, Order, OrderItem
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .models import Category, Product, ProductImage, Brand, Comment
from django.contrib import messages
from django.db import transaction


def get_shipping_settings():
    """دریافت تنظیمات هزینه ارسال"""
    shipping_cost = int(Settings.get_value('shipping_cost', '70000'))
    free_shipping_threshold = int(Settings.get_value('free_shipping_threshold', '500000'))
    return {
        'shipping_cost': shipping_cost,
        'free_shipping_threshold': free_shipping_threshold
    }


def product_list(request):
    """
    This Python function retrieves filter parameters for displaying a list of products with search and
    filtering options.
    
    :param request: The `request` parameter in the `product_list` function is typically an object that
    contains information about the current HTTP request. It includes details such as the request method
    (GET, POST, etc.), headers, user session information, and any data sent in the request (such as form
    data or query
    """
    """نمایش لیست محصولات با فیلتر و جستجو"""
    # Get filter parameters
    category_slug = request.GET.get('category', '')
    brand_slug = request.GET.get('brand', '')
    search_query = request.GET.get('search', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    sort_by = request.GET.get('sort', 'default')
    quick_filter = request.GET.get('quick_filter', '')
    
    
    # Base queryset
    products = Product.objects.filter(is_active=True).select_related('category', 'brand').prefetch_related('images')
    
    # Apply category filter
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    # Apply brand filter
    if brand_slug:
        products = products.filter(brand__slug=brand_slug)
    
    # Apply search filter
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(brand__name__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    # Apply price filters
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass
    
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass
    
    # Apply quick filters
    if quick_filter:
        if quick_filter == 'bestseller':
            products = products.filter(is_bestseller=True)
        elif quick_filter == 'discount':
            products = products.filter(has_discount=True)
        elif quick_filter == 'new':
            products = products.filter(is_new=True)
        elif quick_filter == 'luxury':
            products = products.filter(is_luxury=True)
    
    # Apply sorting
    if sort_by == 'price-low':
        products = products.order_by('price')
    elif sort_by == 'price-high':
        products = products.order_by('-price')
    elif sort_by == 'rating':
        products = products.order_by('-rating')
    elif sort_by == 'name':
        products = products.order_by('name')
    else:
        products = products.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products, 12)  # 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get categories for filter
    categories = Category.objects.filter(is_active=True)
    
    # Get brands for filter
    brands = Brand.objects.filter(is_active=True)
    
    # Get featured products for sidebar
    featured_products = Product.objects.filter(
        is_active=True, 
        is_featured=True
    ).select_related('category', 'brand').prefetch_related('images')[:6]
    
    context = {
        'products': page_obj,
        'categories': categories,
        'brands': brands,
        'featured_products': featured_products,
        'current_category': category_slug,
        'current_brand': brand_slug,
        'search_query': search_query,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
        'quick_filter': quick_filter,
        'total_products': products.count(),
    }
    
    return render(request, 'shop/product_list.html', context)

def product_detail(request, slug):
    """نمایش جزئیات محصول"""
    product = get_object_or_404(
        Product.objects.select_related('category', 'brand').prefetch_related('images', 'specifications'),
        slug=slug,
        is_active=True
    )
    
    # Increment view count
    product.view_count += 1
    product.save(update_fields=['view_count'])
    
    # Get approved comments
    comments = product.comments.filter(is_approved=True).order_by('-created_at')
    
    # Get related products
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id).select_related('category', 'brand').prefetch_related('images')[:4]
    
    # Get similar products (same category or similar price range)
    similar_products = Product.objects.filter(
        is_active=True
    ).exclude(id=product.id).select_related('category', 'brand').prefetch_related('images')[:4]
    
    # Check if product is in user's wishlist
    is_in_wishlist = False
    if request.user.is_authenticated:
        try:
            wishlist = Wishlist.objects.get(user=request.user)
            is_in_wishlist = wishlist.products.filter(id=product.id).exists()
        except Wishlist.DoesNotExist:
            pass
    
    context = {
        'product': product,
        'comments': comments,
        'related_products': related_products,
        'similar_products': similar_products,
        'is_in_wishlist': is_in_wishlist,
    }
    
    return render(request, 'shop/product_detail.html', context)


@csrf_exempt
@require_POST
def add_to_cart(request):
    """افزودن محصول به سبد خرید فعال کاربر. اگر وجود داشته باشد تعداد افزایش می‌یابد."""
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))
    product = get_object_or_404(Product, id=product_id, is_active=True)

    # For now, we'll just return success since we're using localStorage
    # In a real app, you'd handle cart in database
    return JsonResponse({
        'ok': True,
        'message': 'به سبد خرید اضافه شد',
        'item_quantity': quantity,
        'cart_items_count': 1,  # This will be updated by frontend
    })


def get_shipping_settings_api(request):
    """API برای دریافت تنظیمات هزینه ارسال"""
    settings = get_shipping_settings()
    return JsonResponse(settings)


@login_required
@require_POST
@csrf_exempt
def toggle_wishlist(request):
    """افزودن/حذف محصول از علاقه‌مندی‌ها"""
    product_id = request.POST.get('product_id')
    product = get_object_or_404(Product, id=product_id, is_active=True)

    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    added = False
    if wishlist.products.filter(id=product.id).exists():
        wishlist.products.remove(product)
    else:
        wishlist.products.add(product)
        added = True

    return JsonResponse({'ok': True, 'added': added})

def category_products(request, slug):
    """نمایش محصولات یک دسته‌بندی"""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(
        category=category,
        is_active=True
    ).select_related('category', 'brand').prefetch_related('images')
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'products': page_obj,
        'total_products': products.count(),
    }
    
    return render(request, 'shop/category_products.html', context)

def brand_products(request, slug):
    """نمایش محصولات یک برند"""
    brand = get_object_or_404(Brand, slug=slug, is_active=True)
    products = Product.objects.filter(
        brand=brand,
        is_active=True
    ).select_related('category', 'brand').prefetch_related('images')
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'brand': brand,
        'products': page_obj,
        'total_products': products.count(),
    }
    
    return render(request, 'shop/brand_products.html', context)

def featured_products(request):
    """نمایش محصولات ویژه"""
    products = Product.objects.filter(
        is_active=True,
        is_featured=True
    ).select_related('category', 'brand').prefetch_related('images')
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'total_products': products.count(),
        'page_title': 'محصولات ویژه',
    }
    
    return render(request, 'shop/product_list.html', context)

def new_products(request):
    """نمایش محصولات جدید"""
    products = Product.objects.filter(
        is_active=True,
        is_new=True
    ).select_related('category', 'brand').prefetch_related('images')
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'total_products': products.count(),
        'page_title': 'محصولات جدید',
    }
    
    return render(request, 'shop/product_list.html', context)

def bestseller_products(request):
    """نمایش محصولات پرفروش"""
    products = Product.objects.filter(
        is_active=True,
        is_bestseller=True
    ).select_related('category', 'brand').prefetch_related('images')
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'total_products': products.count(),
        'page_title': 'محصولات پرفروش',
    }
    
    return render(request, 'shop/product_list.html', context)

def most_viewed_products(request):
    """نمایش محصولات پربازدید"""
    products = Product.objects.filter(
        is_active=True
    ).select_related('category', 'brand').prefetch_related('images').order_by('-view_count')
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'total_products': products.count(),
        'page_title': 'پربازدیدترین محصولات',
    }
    
    return render(request, 'shop/product_list.html', context)

def search_products(request):
    """جستجوی محصولات"""
    query = request.GET.get('q', '')
    if not query:
        return redirect('shop:product_list')
    
    products = Product.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(brand__name__icontains=query) |
        Q(category__name__icontains=query),
        is_active=True
    ).select_related('category', 'brand').prefetch_related('images')
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'search_query': query,
        'total_products': products.count(),
        'page_title': f'نتایج جستجو برای "{query}"',
    }
    
    return render(request, 'shop/product_list.html', context)

def get_products_json(request):
    """API endpoint برای دریافت محصولات به صورت JSON"""
    products = Product.objects.filter(is_active=True).select_related('category', 'brand').prefetch_related('images')
    
    # Pagination for infinite scroll
    page = request.GET.get('page', 1)
    try:
        page = int(page)
    except ValueError:
        page = 1
    
    paginator = Paginator(products, 12)  # 12 products per page
    try:
        page_obj = paginator.page(page)
    except (EmptyPage, InvalidPage):
        page_obj = paginator.page(paginator.num_pages)
    
    data = []
    for product in page_obj:
        # Get all images for the product
        images = []
        for img in product.images.all():
            images.append({
                'id': img.id,
                'image': img.image.url,
                'alt_text': img.alt_text,
                'is_primary': img.is_primary,
                'order': img.order
            })
        
        data.append({
            'id': product.id,
            'name': product.name,
            'slug': product.slug,
            'price': float(product.price),
            'original_price': float(product.original_price) if product.original_price else None,
            'discount_percentage': product.discount_percentage,
            'has_discount': product.has_discount,
            'category_name': product.category.name,
            'category_slug': product.category.slug,
            'brand_name': product.brand.name if product.brand else None,
            'brand_slug': product.brand.slug if product.brand else None,
            'rating': float(product.rating),
            'review_count': product.review_count,
            'is_bestseller': product.is_bestseller,
            'is_new': product.is_new,
            'is_featured': product.is_featured,
            'is_luxury': product.is_luxury,
            'stock_quantity': product.stock_quantity,
            'images': images,
            'description': product.description,
            'short_description': product.short_description,
            'telegram_link': product.telegram_link,
            'instagram_link': product.instagram_link,
            'facebook_link': product.facebook_link,
        })
    
    return JsonResponse({
        'products': data,
        'has_next': page_obj.has_next(),
        'current_page': page,
        'total_pages': paginator.num_pages,
        'total_products': paginator.count
    })

def get_categories_json(request):
    """API endpoint برای دریافت دسته‌بندی‌ها به صورت JSON"""
    categories = Category.objects.filter(is_active=True)
    
    data = []
    for category in categories:
        data.append({
            'id': category.id,
            'name': category.name,
            'slug': category.slug,
            'products_count': category.get_products_count(),
        })
    
    return JsonResponse({'categories': data})

def get_brands_json(request):
    """API endpoint برای دریافت برندها به صورت JSON"""
    brands = Brand.objects.filter(is_active=True)
    
    data = []
    for brand in brands:
        data.append({
            'id': brand.id,
            'name': brand.name,
            'slug': brand.slug,
            'products_count': brand.get_products_count(),
            'logo_url': brand.logo.url if brand.logo else None,
        })
    
    return JsonResponse({'brands': data})

def test_products(request):
    """تست نمایش محصولات"""
    products = Product.objects.filter(is_active=True).select_related('category', 'brand')
    
    context = {
        'products': products,
        'total_products': products.count(),
    }
    
    return render(request, 'shop/test_products.html', context)

@csrf_exempt
@require_POST
def add_comment(request, product_id):
    """ثبت نظر جدید"""
    try:
        product = get_object_or_404(Product, id=product_id, is_active=True)
        
        # دریافت داده‌ها از فرم
        rating = request.POST.get('rating', '')
        comment_text = request.POST.get('comment', '').strip()
        
        # اعتبارسنجی داده‌ها
        if not rating or not comment_text:
            return JsonResponse({
                'success': False,
                'message': 'لطفاً امتیاز و نظر خود را وارد کنید.'
            })
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError()
        except ValueError:
            return JsonResponse({
                'success': False,
                'message': 'امتیاز باید بین 1 تا 5 باشد.'
            })
        
        # دریافت اطلاعات کاربر
        if request.user.is_authenticated:
            name = f"{request.user.first_name} {request.user.last_name}".strip()
            if not name:
                name = request.user.username
            email = request.user.email
        else:
            name = "کاربر مهمان"
            email = "guest@example.com"
        
        # ایجاد کامنت جدید
        comment = Comment.objects.create(
            product=product,
            user=request.user if request.user.is_authenticated else None,
            name=name,
            email=email,
            rating=rating,
            comment=comment_text,
            is_approved=True  # برای تست، همه کامنت‌ها تایید می‌شوند
        )
        
        # بروزرسانی امتیاز محصول
        product.update_rating()
        
        return JsonResponse({
            'success': True,
            'message': 'نظر شما با موفقیت ثبت شد.',
            'comment': {
                'name': comment.name,
                'rating': comment.rating,
                'comment': comment.comment,
                'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M'),
                'user_avatar': comment.user.profile.avatar.url if comment.user and comment.user.profile.avatar else None
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'خطا در ثبت نظر. لطفاً دوباره تلاش کنید.'
        })


def cart_view(request):
    """نمایش سبد خرید بر اساس تمپلیت موجود در home.html (سکشن Cart Page) اما در صفحه جداگانه."""
    # این صفحه بیشتر فرانت‌اندی است؛ اقلام سبد خرید سمت کلاینت رندر می‌شود
    # در صورت نیاز می‌توان داده‌های اولیه را از دیتابیس هم ارسال کرد
    shipping_settings = get_shipping_settings()
    context = {
        'shipping_settings': shipping_settings
    }
    return render(request, 'shop/cart.html', context)


@login_required
def checkout(request):
    """صفحه تکمیل خرید"""
    shipping_settings = get_shipping_settings()
    # پر کردن اولیه فرم از پروفایل کاربر
    user = request.user
    initial = {
        'receiver_name': f"{user.first_name} {user.last_name}".strip(),
        'receiver_phone': user.phone or '',
        'province_name': getattr(user.province, 'name', ''),
        'city_name': getattr(user.city, 'name', ''),
        'address_detail': user.address or '',
        'province_name': getattr(user.province, 'name', ''),
        'city_name': getattr(user.city, 'name', ''),
    }
    context = {
        'shipping_settings': shipping_settings,
        'initial': initial,
    }
    return render(request, 'shop/checkout.html', context)


@login_required
@require_POST
@csrf_exempt
def process_order(request):
    """پردازش سفارش و ایجاد فاکتور"""
    try:
        with transaction.atomic():
            # دریافت داده‌های سفارش
            receiver_name = request.POST.get('receiver_name', '').strip()
            receiver_phone = request.POST.get('receiver_phone', '').strip()
            province_name = request.POST.get('province_name', '').strip()
            city_name = request.POST.get('city_name', '').strip()
            address_detail = request.POST.get('address_detail', '').strip()
            postal_code = request.POST.get('postal_code', '').strip()
            
            # اعتبارسنجی داده‌ها
            if not all([receiver_name, receiver_phone, province_name, city_name, address_detail, postal_code]):
                return JsonResponse({
                    'success': False,
                    'message': 'لطفاً تمام فیلدهای ضروری را پر کنید.'
                })
            
            # دریافت اقلام سبد خرید از localStorage (در فرانت‌اند)
            cart_data = request.POST.get('cart_data', '[]')
            import json
            try:
                cart_items = json.loads(cart_data)
            except json.JSONDecodeError:
                return JsonResponse({
                    'success': False,
                    'message': 'خطا در پردازش سبد خرید.'
                })
            
            if not cart_items:
                return JsonResponse({
                    'success': False,
                    'message': 'سبد خرید شما خالی است.'
                })
            
            # محاسبه مبالغ
            subtotal = 0
            shipping_settings = get_shipping_settings()
            
            # بررسی موجودی و محاسبه قیمت‌ها
            order_items_data = []
            for item in cart_items:
                try:
                    product = Product.objects.get(id=item['id'], is_active=True)
                    
                    # بررسی موجودی
                    if product.stock_quantity < item['quantity']:
                        return JsonResponse({
                            'success': False,
                            'message': f'موجودی محصول "{product.name}" کافی نیست. موجودی: {product.stock_quantity}'
                        })
                    
                    # محاسبه قیمت
                    unit_price = float(product.price)
                    total_price = unit_price * item['quantity']
                    subtotal += total_price
                    
                    order_items_data.append({
                        'product': product,
                        'quantity': item['quantity'],
                        'unit_price': unit_price,
                        'total_price': total_price
                    })
                    
                except Product.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'message': f'محصول با شناسه {item["id"]} یافت نشد.'
                    })
            
            # محاسبه هزینه ارسال
            shipping_cost = shipping_settings['shipping_cost']
            if subtotal >= shipping_settings['free_shipping_threshold']:
                shipping_cost = 0
            
            total_amount = subtotal + shipping_cost
            
            # ایجاد سفارش
            order = Order.objects.create(
                user=request.user,
                status='pending',
                subtotal_amount=subtotal,
                shipping_amount=shipping_cost,
                total_amount=total_amount,
                receiver_name=receiver_name,
                receiver_phone=receiver_phone,
                province_name=province_name,
                city_name=city_name,
                address_detail=address_detail,
                postal_code=postal_code
            )
            
            # ایجاد آیتم‌های سفارش و کاهش موجودی
            for item_data in order_items_data:
                OrderItem.objects.create(
                    order=order,
                    product=item_data['product'],
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price'],
                    total_price=item_data['total_price']
                )
                
                # کاهش موجودی محصول
                product = item_data['product']
                product.stock_quantity -= item_data['quantity']
                product.save()
            
            # ارسال پیام موفقیت
            messages.success(request, f'سفارش شما با شماره #{order.id} با موفقیت ثبت شد.')
            
            # ارسال پیام به ترمینال
            print(f"🛒 سفارش جدید ثبت شد!")
            print(f"   شماره سفارش: #{order.id}")
            print(f"   کاربر: {request.user.username}")
            print(f"   مبلغ کل: {total_amount:,} تومان")
            print(f"   تعداد آیتم‌ها: {len(order_items_data)}")
            print(f"   تاریخ: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 50)
            
            return JsonResponse({
                'success': True,
                'message': f'سفارش شما با شماره #{order.id} با موفقیت ثبت شد.',
                'order_id': order.id,
                'redirect_url': f'/shop/order/{order.id}/'
            })
            
    except Exception as e:
        print(f"خطا در پردازش سفارش: {e}")
        return JsonResponse({
            'success': False,
            'message': 'خطا در پردازش سفارش. لطفاً دوباره تلاش کنید.'
        })


def order_detail(request, order_id):
    """نمایش جزئیات سفارش"""
    if not request.user.is_authenticated:
        return redirect('core:login')
    
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {
        'order': order
    }
    return render(request, 'shop/order_detail.html', context)


@login_required
def pay_order(request, order_id):
    """شبیه‌سازی شروع پرداخت: کاربر به درگاه فرضی هدایت می‌شود و سپس به همان سفارش باز می‌گردد.
    در محیط واقعی این‌جا توکن درگاه ایجاد و ریدایرکت انجام می‌شود."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # اگر سفارش قبلاً پرداخت شده است، برگردیم به جزئیات
    if order.status == 'paid':
        messages.info(request, 'این سفارش قبلاً پرداخت شده است.')
        return redirect('shop:order_detail', order_id=order.id)
    
    # شبیه‌سازی پرداخت موفق
    order.status = 'paid'
    order.save(update_fields=['status'])
    
    messages.success(request, f'پرداخت سفارش #{order.id} با موفقیت انجام شد.')
    return redirect('shop:order_detail', order_id=order.id)
