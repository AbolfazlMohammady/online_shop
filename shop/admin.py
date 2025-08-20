from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib.admin import AdminSite
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import Category, Product, ProductImage, ProductSpecification, Brand, Comment, Cart, CartItem, Wishlist, Order, OrderItem, Settings, Banner, ShippingSettings

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
    max_num = 5
    verbose_name = "کامنت"
    verbose_name_plural = "کامنت‌ها"
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def get_queryset(self, request):
        # فقط 5 کامنت آخر را نمایش بده
        qs = super().get_queryset(request)
        return qs.order_by('-created_at')

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
        'stock_quantity', 'rating', 'is_active', 'is_featured', 'is_bestseller', 'get_social_links'
    ]
    list_filter = [
        'category', 'brand', 'is_active', 'is_featured', 'is_bestseller', 'is_new', 
        'is_luxury', 'has_discount', 'status', 'created_at'
    ]
    search_fields = ['name', 'description', 'brand__name', 'model']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['rating', 'review_count', 'created_at', 'updated_at', 'get_comments_summary']
    inlines = [ProductImageInline, ProductSpecificationInline]
    
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
        ('امتیازات و کامنت‌ها', {
            'fields': ('rating', 'review_count', 'get_comments_summary')
        }),
        ('وضعیت', {
            'fields': ('status', 'is_active')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('شبکه‌های اجتماعی', {
            'fields': ('telegram_link', 'instagram_link', 'facebook_link'),
            'classes': ('collapse',)
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_comments_summary(self, obj):
        """نمایش خلاصه کامنت‌ها"""
        comments_count = obj.comments.count()
        if comments_count == 0:
            return "بدون کامنت"
        
        approved_count = obj.comments.filter(is_approved=True).count()
        pending_count = comments_count - approved_count
        
        summary = f"کل: {comments_count} | تایید شده: {approved_count}"
        if pending_count > 0:
            summary += f" | در انتظار: {pending_count}"
        
        # لینک به صفحه کامنت‌ها
        admin_url = reverse('admin:shop_comment_changelist')
        filter_url = f"{admin_url}?product__id__exact={obj.id}"
        
        return format_html(
            '{}<br><a href="{}" target="_blank" style="color: #007cba; font-size: 12px;">مشاهده همه کامنت‌ها</a>',
            summary, filter_url
        )
    get_comments_summary.short_description = 'خلاصه کامنت‌ها'
    
    def get_social_links(self, obj):
        links = []
        if obj.telegram_link:
            links.append(f'<a href="{obj.telegram_link}" target="_blank" style="color: #0088cc; margin-left: 5px;"><i class="fab fa-telegram"></i></a>')
        if obj.instagram_link:
            links.append(f'<a href="{obj.instagram_link}" target="_blank" style="color: #e4405f; margin-left: 5px;"><i class="fab fa-instagram"></i></a>')
        if obj.facebook_link:
            links.append(f'<a href="{obj.facebook_link}" target="_blank" style="color: #1877f2; margin-left: 5px;"><i class="fab fa-facebook"></i></a>')
        
        if links:
            return format_html(''.join(links))
        return "بدون لینک"
    get_social_links.short_description = 'شبکه‌های اجتماعی'
    
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


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_active', 'created_at', 'updated_at', 'total']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at']

    def total(self, obj):
        return f"{obj.get_total_amount():,}"


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity', 'price', 'created_at']
    list_filter = ['created_at', 'product__category']
    search_fields = ['product__name', 'cart__user__email']


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'products_count']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']

    def products_count(self, obj):
        return obj.products.count()


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total_amount', 'payment_status', 'created_at']
    list_filter = ['status', 'created_at', 'payment_date']
    search_fields = ['user__email', 'receiver_name', 'receiver_phone']
    inlines = [OrderItemInline]
    readonly_fields = ['created_at', 'payment_date']
    
    fieldsets = (
        ('اطلاعات سفارش', {
            'fields': ('user', 'status', 'created_at')
        }),
        ('مبالغ', {
            'fields': ('subtotal_amount', 'shipping_amount', 'total_amount')
        }),
        ('اطلاعات ارسال', {
            'fields': ('receiver_name', 'receiver_phone', 'province_name', 'city_name', 'address_detail', 'postal_code')
        }),
        ('اطلاعات پرداخت', {
            'fields': ('payment_authority', 'payment_ref_id', 'payment_status_code', 'payment_description', 'payment_date'),
            'classes': ('collapse',)
        }),
    )
    
    def payment_status(self, obj):
        if obj.status == 'paid':
            return format_html('<span style="color: green;">✓ پرداخت شده</span>')
        elif obj.status == 'payment_failed':
            return format_html('<span style="color: red;">✗ پرداخت ناموفق</span>')
        elif obj.status == 'pending':
            return format_html('<span style="color: orange;">⏳ در انتظار پرداخت</span>')
        else:
            return obj.get_status_display()
    payment_status.short_description = "وضعیت پرداخت"


@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = ['key', 'value', 'description', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['key', 'value', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['key']


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'banner_type', 'image_preview', 'discount_percentage', 'countdown_hours', 'is_active', 'created_at']
    list_filter = ['banner_type', 'is_active', 'created_at']
    search_fields = ['title', 'subtitle']
    list_editable = ['is_active', 'discount_percentage', 'countdown_hours']
    readonly_fields = ['created_at', 'updated_at', 'countdown_end_time', 'is_expired', 'image_preview']
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'subtitle', 'image', 'banner_type', 'is_active')
        }),
        ('تنظیمات دکمه', {
            'fields': ('button_text', 'button_url')
        }),
        ('تنظیمات تخفیف', {
            'fields': ('discount_percentage', 'countdown_hours')
        }),
        ('پیش‌نمایش', {
            'fields': ('image_preview',),
            'classes': ('collapse',)
        }),
        ('اطلاعات زمانی', {
            'fields': ('created_at', 'updated_at', 'countdown_end_time', 'is_expired'),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 200px;" />', obj.image.url)
        return "بدون تصویر"
    image_preview.short_description = "پیش‌نمایش تصویر"
    
    def countdown_end_time(self, obj):
        return obj.countdown_end_time
    countdown_end_time.short_description = "زمان پایان شمارش معکوس"
    
    def is_expired(self, obj):
        return obj.is_expired
    is_expired.boolean = True
    is_expired.short_description = "منقضی شده"


@admin.register(ShippingSettings)
class ShippingSettingsAdmin(admin.ModelAdmin):
    list_display = ['shipping_cost', 'free_shipping_threshold']
    list_editable = ['free_shipping_threshold']
    list_display_links = ['shipping_cost']

