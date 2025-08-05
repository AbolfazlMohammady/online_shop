from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from .models import Category, Product, ProductImage, Brand

# Create your views here.

def product_list(request):
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
    
    # Get related products
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id).select_related('category', 'brand').prefetch_related('images')[:4]
    
    # Get similar products (same category or similar price range)
    similar_products = Product.objects.filter(
        is_active=True
    ).exclude(id=product.id).select_related('category', 'brand').prefetch_related('images')[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
        'similar_products': similar_products,
    }
    
    return render(request, 'shop/product_detail.html', context)

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
    
    data = []
    for product in products:
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
            'price': str(product.price),
            'original_price': str(product.original_price) if product.original_price else None,
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
            'images': images,
            'description': product.description,
            'short_description': product.short_description,
        })
    
    return JsonResponse({'products': data})

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
