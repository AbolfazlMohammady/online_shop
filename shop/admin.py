from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib.admin import AdminSite
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import Category, Product, ProductImage, ProductSpecification, Brand, Comment

# Custom Admin Site
class BeautyShopAdminSite(AdminSite):
    site_header = "زیبایی شاپ - پنل مدیریت"
    site_title = "زیبایی شاپ"
    index_title = "خوش آمدید به پنل مدیریت زیبایی شاپ"

admin_site = BeautyShopAdminSite(name='beautyshop_admin')

# Dashboard Widgets
class CommentStatsWidget(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        # Get comment statistics
        total_comments = Comment.objects.count()
        approved_comments = Comment.objects.filter(is_approved=True).count()
        pending_comments = Comment.objects.filter(is_approved=False).count()
        
        # Recent comments (last 7 days)
        week_ago = timezone.now() - timedelta(days=7)
        recent_comments = Comment.objects.filter(created_at__gte=week_ago).count()
        
        # Average rating
        avg_rating = Comment.objects.filter(is_approved=True).aggregate(
            avg_rating=Count('rating')
        )['avg_rating'] or 0
        
        extra_context = extra_context or {}
        extra_context.update({
            'total_comments': total_comments,
            'approved_comments': approved_comments,
            'pending_comments': pending_comments,
            'recent_comments': recent_comments,
            'avg_rating': avg_rating,
        })
        
        return super().changelist_view(request, extra_context)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'caption', 'is_primary', 'order']

class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 1
    fields = ['name', 'value', 'order']

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ['name', 'email', 'rating', 'comment', 'created_at']
    fields = ['name', 'rating', 'comment', 'is_approved', 'created_at']
    can_delete = False
    max_num = 10
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'get_products_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']
    
    def get_products_count(self, obj):
        return obj.get_products_count()
    get_products_count.short_description = 'تعداد محصولات'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'get_products_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']
    
    def get_products_count(self, obj):
        return obj.get_products_count()
    get_products_count.short_description = 'تعداد محصولات'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'brand', 'price', 'original_price', 'discount_percentage', 
        'stock_quantity', 'rating', 'is_active', 'is_featured', 'is_bestseller'
    ]
    list_filter = [
        'category', 'brand', 'is_active', 'is_featured', 'is_bestseller', 'is_new', 
        'is_luxury', 'has_discount', 'status', 'created_at'
    ]
    search_fields = ['name', 'description', 'brand__name', 'model']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['rating', 'review_count', 'created_at', 'updated_at']
    inlines = [ProductImageInline, ProductSpecificationInline, CommentInline]
    
    fieldsets = (
        ('اطلاعات پایه', {
            'fields': ('name', 'slug', 'category', 'brand', 'description', 'short_description')
        }),
        ('قیمت‌گذاری', {
            'fields': ('price', 'original_price', 'discount_percentage', 'discount_amount')
        }),
        ('موجودی', {
            'fields': ('stock_quantity', 'min_stock_alert')
        }),
        ('جزئیات محصول', {
            'fields': ('model', 'color', 'size', 'weight', 'dimensions')
        }),
        ('ویژگی‌ها', {
            'fields': ('is_featured', 'is_bestseller', 'is_new', 'is_luxury', 'has_discount')
        }),
        ('امتیازات', {
            'fields': ('rating', 'review_count')
        }),
        ('وضعیت', {
            'fields': ('status', 'is_active')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if obj.discount_percentage > 0 and not obj.original_price:
            obj.original_price = obj.price
        super().save_model(request, obj, form, change)

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image_preview', 'is_primary', 'order', 'created_at']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['product__name', 'caption', 'alt_text']
    ordering = ['product', 'order']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.image.url)
        return "بدون تصویر"
    image_preview.short_description = 'پیش‌نمایش'

@admin.register(ProductSpecification)
class ProductSpecificationAdmin(admin.ModelAdmin):
    list_display = ['product', 'name', 'value', 'order']
    list_filter = ['product__category']
    search_fields = ['product__name', 'name', 'value']
    ordering = ['product', 'order']

@admin.register(Comment)
class CommentAdmin(CommentStatsWidget):
    list_display = [
        'get_user_avatar', 'name', 'get_product_link', 'rating_stars', 
        'is_approved', 'created_at', 'get_time_ago'
    ]
    list_filter = [
        'is_approved', 'rating', 'created_at', 'product__category', 'product__brand'
    ]
    search_fields = [
        'name', 'email', 'comment', 'product__name', 'user__username', 'user__first_name', 'user__last_name'
    ]
    readonly_fields = ['created_at', 'updated_at', 'get_user_avatar', 'get_product_link']
    list_editable = ['is_approved']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('اطلاعات کاربر', {
            'fields': ('get_user_avatar', 'name', 'email', 'user')
        }),
        ('محصول', {
            'fields': ('get_product_link', 'product')
        }),
        ('نظر و امتیاز', {
            'fields': ('rating', 'comment')
        }),
        ('وضعیت', {
            'fields': ('is_approved',)
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_user_avatar(self, obj):
        if obj.user and obj.user.profile_image:
            return format_html(
                '<img src="{}" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover;" />',
                obj.user.profile_image.url
            )
        else:
            return format_html(
                '<div style="width: 40px; height: 40px; border-radius: 50%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 16px;">{}</div>',
                obj.name[0].upper() if obj.name else '?'
            )
    get_user_avatar.short_description = 'آواتار'
    
    def get_product_link(self, obj):
        if obj.product:
            url = reverse('admin:shop_product_change', args=[obj.product.id])
            return format_html('<a href="{}">{}</a>', url, obj.product.name)
        return "محصول نامشخص"
    get_product_link.short_description = 'محصول'
    
    def rating_stars(self, obj):
        stars = ''
        for i in range(1, 6):
            if i <= obj.rating:
                stars += '<i class="fas fa-star" style="color: #fbbf24;"></i>'
            else:
                stars += '<i class="far fa-star" style="color: #d1d5db;"></i>'
        return format_html('<div style="font-size: 14px;">{} <span style="color: #6b7280; margin-right: 5px;">({}/5)</span></div>', mark_safe(stars), obj.rating)
    rating_stars.short_description = 'امتیاز'
    
    def get_time_ago(self, obj):
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff.days > 0:
            return f"{diff.days} روز پیش"
        elif diff.seconds >= 3600:
            hours = diff.seconds // 3600
            return f"{hours} ساعت پیش"
        elif diff.seconds >= 60:
            minutes = diff.seconds // 60
            return f"{minutes} دقیقه پیش"
        else:
            return "چند ثانیه پیش"
    get_time_ago.short_description = 'زمان'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product', 'user')
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Update product rating when comment is approved/unapproved
        if 'is_approved' in form.changed_data:
            obj.product.update_rating()
    
    actions = ['approve_comments', 'disapprove_comments', 'delete_selected']
    
    def approve_comments(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} نظر تایید شد.')
        # Update ratings for affected products
        for comment in queryset:
            comment.product.update_rating()
    approve_comments.short_description = 'تایید نظرات انتخاب شده'
    
    def disapprove_comments(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} نظر رد شد.')
        # Update ratings for affected products
        for comment in queryset:
            comment.product.update_rating()
    disapprove_comments.short_description = 'رد نظرات انتخاب شده'
    
    class Media:
        css = {
            'all': ('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',)
        }
