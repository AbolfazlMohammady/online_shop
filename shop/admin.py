from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductImage, ProductSpecification, Brand

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'caption', 'is_primary', 'order']

class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 1
    fields = ['name', 'value', 'order']

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
